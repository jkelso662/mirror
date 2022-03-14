# content of test_sample.py
from mirror.github.queries import *


def test_should_return_query_with_year():
    assert get_new_repos(2025) == QUERY_WITH_YEAR


def test_should_return_query_with_year_and_cursor():
    assert get_new_repos(2035, "Y3Vyc29yOjIwNA==") == QUERY_WITH_YEAR_AND_CURSOR


def test_should_error_on_invalid_cursor():
    pass


def test_should_error_on_invalid_year():
    pass


def test_should_return_custom_query():
    assert get_new_repos_custom_query(">500") == CUSTOM_QUERY


def test_should_return_custom_query_with_year_and_cursor():
    assert get_new_repos_custom_query(">500", "Y3Vyc29yOjIwNA==") == CUSTOM_QUERY_WITH_YEAR_AND_CURSOR


def test_should_error_on_invalid_cursor():
    pass


def test_should_error_on_invalid_year():
    pass


def test_should_return_repo_by_id():
    assert get_repo("MDEwOlJlcG9zaXRvcnkxODEyMDQwMDI") == REPO_BY_ID_QUERY


QUERY_WITH_YEAR = """{
search(query: ">2025-01-01", type: REPOSITORY, first: 100) {
  repositoryCount
  edges {
    cursor
    node {
      ... on Repository {
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {
          field: SIZE,
          direction: DESC
        }) {
          totalCount
          edges {
            size
            node {
              name
            }
          }
        }
        stargazers {
          totalCount
        }
        forkCount
        updatedAt
        createdAt
      }
    }
  }
}
rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}
}"""

QUERY_WITH_YEAR_AND_CURSOR = """{
search(query: ">2035-01-01", type: REPOSITORY, first: 100, after: "Y3Vyc29yOjIwNA==") {
  repositoryCount
  edges {
    cursor
    node {
      ... on Repository {
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {
          field: SIZE,
          direction: DESC
        }) {
          totalCount
          edges {
            size
            node {
              name
            }
          }
        }
        stargazers {
          totalCount
        }
        forkCount
        updatedAt
        createdAt
      }
    }
  }
}
rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}
}"""

CUSTOM_QUERY = """{
search(query: ">500", type: REPOSITORY, first: 100) {
  repositoryCount
  edges {
    cursor
    node {
      ... on Repository {
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {
          field: SIZE,
          direction: DESC
        }) {
          totalCount
          edges {
            size
            node {
              name
            }
          }
        }
        stargazers {
          totalCount
        }
        forkCount
        updatedAt
        createdAt
      }
    }
  }
}
rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}
}"""

CUSTOM_QUERY_WITH_YEAR_AND_CURSOR = """{
search(query: ">500", type: REPOSITORY, first: 100, after: "Y3Vyc29yOjIwNA==") {
  repositoryCount
  edges {
    cursor
    node {
      ... on Repository {
        id
        name
        description
        shortDescriptionHTML
        primaryLanguage {
          name
        }
        languages(first: 10, orderBy: {
          field: SIZE,
          direction: DESC
        }) {
          totalCount
          edges {
            size
            node {
              name
            }
          }
        }
        stargazers {
          totalCount
        }
        forkCount
        updatedAt
        createdAt
      }
    }
  }
}
rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}
}"""

REPO_BY_ID_QUERY = """{
node(id: "MDEwOlJlcG9zaXRvcnkxODEyMDQwMDI"){
  ... on Repository {
    id
    nameWithOwner
    stargazers {
      totalCount
    }
    forkCount
  }
}
rateLimit {
  limit     # Your maximum budget. Your budget is reset to this every hour.
  cost      # The cost of this query.
  remaining # How much of your API budget remains.
  resetAt   # The time (in UTC epoch seconds) when your budget will reset.
}
}"""