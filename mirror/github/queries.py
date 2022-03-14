"""
GraphQL queries
"""

# TODO(jk): Incorporate more explicit date range
limits_query = """rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}"""


def get_test():
    # https://gist.github.com/gbaman/b3137e18c739e0cf98539bf4ec4366ad
    variables = {
        'queryString': 'is:public stars:>9999',
        'maxItems': '5'
    }
    return """
{{
   search(query: "{queryString}", type: REPOSITORY, first: {maxItems}) {{
     repositoryCount
     edges {{
       node {{
         ... on Repository {{
           name
           url
           stargazers {{ totalCount }}
         }}
       }}
    }}
  }}
}}""".format(**variables)


def get_new_repos(year=2021, cursor=""):
    cursor_str = cursor if cursor == "" else f', after: \"{cursor}\"'
    return """{{
search(query: ">{year}-01-01", type: REPOSITORY, first: 100{cursor_str}) {{
  repositoryCount
  edges {{
    cursor
    node {{
      ... on Repository {{
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {{
          name
        }}
        languages(first: 10, orderBy: {{
          field: SIZE,
          direction: DESC
        }}) {{
          totalCount
          edges {{
            size
            node {{
              name
            }}
          }}
        }}
        stargazers {{
          totalCount
        }}
        forkCount
        updatedAt
        createdAt
      }}
    }}
  }}
}}
{limits_query}
}}""".format(year=year, cursor_str=cursor_str, limits_query=limits_query)


def get_new_repos_custom_query(query, cursor=""):
    cursor_str = cursor if cursor == "" else f', after: \"{cursor}\"'
    return """{{
search(query: "{query}", type: REPOSITORY, first: 100{cursor_str}) {{
  repositoryCount
  edges {{
    cursor
    node {{
      ... on Repository {{
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {{
          name
        }}
        languages(first: 10, orderBy: {{
          field: SIZE,
          direction: DESC
        }}) {{
          totalCount
          edges {{
            size
            node {{
              name
            }}
          }}
        }}
        stargazers {{
          totalCount
        }}
        forkCount
        updatedAt
        createdAt
      }}
    }}
  }}
}}
{limits_query}
}}""".format(query=query, cursor_str=cursor_str, limits_query=limits_query)


def get_repo(id):
    return """{{
node(id: "{id}"){{
  ... on Repository {{
    id
    nameWithOwner
    stargazers {{
      totalCount
    }}
    forkCount
  }}
}}
{limits_query}
}}""".format(id=id, limits_query=limits_query)


def get_repos(year=2021, cursor=""):
    cursor_str = cursor if cursor == "" else f', after: \"{cursor}\"'
    return """{{
search(query: ">{year}-01-01", type: REPOSITORY, first: 100{cursor_str}) {{
  repositoryCount
  edges {{
    cursor
    node {{
      ... on Repository {{
        id
        name
        stargazers {{
          totalCount
        }}
        forkCount
        updatedAt
      }}
    }}
  }}
}}
{limits_query}
}}""".format(year=year, cursor_str=cursor_str, limits_query=limits_query)
