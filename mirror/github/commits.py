import re
import os
import csv
import sys
import json
import time
import glob
import zipfile
import string
import traceback
from pathlib import Path
from typing import Optional

from .utils import flatten_json, get_nearest_value

import requests
import click

from .utils import write_with_size, read_command_type
from .data import CommitPublic


class MaskStructureError(Exception):
    """Raised when mask missmatch with input json."""

    pass


REMAINING_RATELIMIT_HEADER = "X-RateLimit-Remaining"

DATETIME_HEADER = "Date"


validate_models = {"CommitPublic": CommitPublic}


def validate(data, allowed_data, schema):
    """Take a data structure and apply pydentic model."""
    pydentic_class = validate_models[schema]
    allowed_data.update(pydentic_class(**data).dict())


def commits_parser(github_commits, repo_id, html_url, schema):

    """
    Push commits via validator and add additional fileds.
    return list of json string
    """
    commits = github_commits.json()

    out = list()

    for commit in commits:

        allowed_data = {"repo_id": repo_id, "repo_html_url": html_url}

        if commit:
            validate(flatten_json(commit), allowed_data, schema)

        out.append(json.dumps(allowed_data))

    return commits[0]["sha"], out


def read_repos(repos_dir, file_name, start_id, end_id):
    """
    Read repos from file. Filter repos by given repo id range if specified.
    """
    repos_file_path = os.path.join(repos_dir, file_name)

    # load available repo
    if os.path.isfile(repos_file_path):
        with open(repos_file_path, "r") as repos_file:
            if start_id and end_id:
                return [
                    repo for repo in json.loads(repos_file.read())["data"] if repo["id"]
                ]
            else:
                return json.loads(repos_file.read())["data"]


def create_zip_file(files_dir):
    """
    Create zip inside snippets folder
    """
    with zipfile.ZipFile(
        os.path.join(files_dir, "..", "commits.zip"), "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        for root, dirs, files in os.walk(files_dir):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file), os.path.join(files_dir, "..")
                    ),
                )


def request_with_limit(repo, headers, min_rate_limit):
    """
    Request to github api do simple awaite if request limit close to cli specified limit
    """

    while True:

        response = requests.get(
            repo["commits_url"].replace("{/sha}", ""), headers=headers
        )

        rate_limit_raw = response.headers.get(REMAINING_RATELIMIT_HEADER)

        if rate_limit_raw is not None:
            current_rate_limit = int(rate_limit_raw)
            if current_rate_limit <= min_rate_limit:

                print("Rate limit is end. Awaiting 1 minute.")
                time.sleep(60)
            else:
                break
        else:
            raise ("incorrect commit URL")
    return response


def get_repos_files(repos_dir, start_id, end_id):

    """
    Return list of files with repose by given ids range or all files from folder if ids range not set

    In order to make sure that all repositories are covered,
    add 2 additional files from the beginning of the ordered directory list and from the end

    """

    dir_files = os.listdir(repos_dir)

    if not dir_files:
        raise ("Empty repos dir.")

    result_command_type = read_command_type(os.path.join(repos_dir, dir_files[0]))

    if start_id and end_id and result_command_type == "crawl":

        nerest_start_id = get_nearest_value(dir_files, start_id)

        if dir_files.index(f"{nerest_start_id}.json") - 2 <= 0:
            start_index = 0
        else:
            start_file = dir_files.index(f"{nerest_start_id}.json") - 2

        nerest_end_id = get_nearest_value(dir_files, end_id)

        if dir_files.index(f"{nerest_end_id}.json") + 2 >= len(dir_files):
            end_index = -1
        else:
            end_index = dir_files.index(f"{nerest_end_id}.json") + 2

    else:
        return dir_files


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--start-id",
    "-s",
    type=int,
    default=None,
    help="Start repo id for crawl command output.",
)
@click.option(
    "--end-id",
    "-e",
    type=int,
    default=None,
    help="End repo id. You need to specify both parameters start and end id. ",
)
@click.option("--crawldir", "-d", default=".", help='Path to save folder. default="." ')
@click.option("--repos-dir", "-r", help="Directory with repos files.")
@click.option(
    "--schema",
    "-S",
    type=click.Choice(list(validate_models.keys())),
    default="CommitPublic",
    help="Directory with repos files."
)
@click.option(
    "--token",
    "-t",
    help="Access token for increase rate limit. Read from env $github_token if specify.",
    default=None,
)
@click.option(
    "--min-rate-limit",
    "-l",
    type=int,
    default=10,
    help="Minimum remaining rate limit on API under which the crawl is interrupted",
)
def commits(
    start_id: Optional[int],
    end_id: Optional[int],
    crawldir: str,
    repos_dir: str,
    schema: str,
    token: Optional[str],
    min_rate_limit: int
):

    """
    Read repos json file and upload all commits for that repos one by one.
    """

    if not os.path.exists(crawldir):
        os.makedirs(crawldir)

    if not token:
        if os.environ.get("GITHUB_TOKEN"):
            token = os.environ.get("GITHUB_TOKEN")
        else:
            click.echo(f"start with low rate limit")

    headers = {
        "accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    file_index = 1

    files_for_proccessing = get_repos_files(repos_dir, start_id, end_id)

    start_block = '{ "command": "commits", "data": ['

    # 2 output idexing csv and commits
    commits_out = os.path.join(crawldir, "commits")

    csv_out = os.path.join(commits_out, "id_indexes.csv")

    if not os.path.exists(commits_out):
        os.makedirs(commits_out)

    with click.progressbar(files_for_proccessing) as bar, open(
        csv_out, mode="wt", encoding="utf8", newline=""
    ) as output:

        fnames = ["file", "commt_hash", "license", "repo_url", "language"]

        writer = csv.DictWriter(output, fieldnames=fnames)
        writer.writeheader()

        for file_name in bar:

            repos = read_repos(repos_dir, file_name, start_id, end_id)

            if not repos:
                continue

            write_with_size(start_block, file_index, commits_out)

            for i, repo in enumerate(repos):

                # Get commits
                commits_responce = request_with_limit(repo, headers, min_rate_limit)

                sha, commits = commits_parser(
                    commits_responce, repo["id"], repo["html_url"], schema
                )

                repo_dump = ",".join(commits)

                if repo["license"]:
                    license = repo["license"]["spdx_id"]
                else:
                    license = repo["license"]

                # date of creating that commits file
                date = commits_responce.headers.get(DATETIME_HEADER)

                # Indexing
                writer.writerow(
                    {
                        "file": os.path.join("commits", f"{file_index}.json"),
                        "repo_url": repo["html_url"],
                        "commt_hash": sha,
                        "license": license,
                        "language": repo["language"]
                    }
                )

                current_size = write_with_size(repo_dump, file_index, commits_out)

                # Size regulation
                if current_size > 5000000:

                    write_with_size(
                        f'], "crawled_at": "{date}" {"}"}', file_index, commits_out
                    )
                    file_index += 1
                    write_with_size(start_block, file_index, commits_out)
                elif i == len(repos) - 1:
                    write_with_size(
                        f'], "crawled_at": "{date}" {"}"}', file_index, commits_out
                    )
                    file_index += 1
                else:
                    write_with_size(",", file_index, commits_out)
    create_zip_file(commits_out)


if __name__ == "__main__":
    commits()
