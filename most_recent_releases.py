from xml.dom import pulldom
from python_graphql_client import GraphqlClient
import os
import re

client = GraphqlClient(endpoint="https://api.github.com/graphql")
TOKEN = os.environ.get("PAT", "")

organization_graphql = """
  organization(login: "tacosdedatos") {
    repositories(first: 100, privacy: PUBLIC) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        description
        url
        releases(last: 2) {
          totalCount
          nodes {
            isDraft
            isPrerelease
            name
            publishedAt
            url
          }
        }
      }
    }
  }
  """


def make_query(after_cursor=None, include_organization=False):
    return """
query {
  ORGANIZATION
  viewer {
    repositories(first: 100, privacy: PUBLIC, after: AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        description
        url
        releases(last: 2) {
          totalCount
          nodes {
            isDraft
            isPrerelease
            name
            publishedAt
            url
          }
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    ).replace(
        "ORGANIZATION",
        organization_graphql if include_organization else "",
    )


def fetch_releases(oauth_token):
    repos = []
    releases = []
    repo_names = {"playing-with-actions"}  # Skip this one
    has_next_page = True
    after_cursor = None

    first = True

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor, include_organization=first),
            headers={"Authorization": "Bearer {}".format(oauth_token)},
        )
        first = False
        repo_nodes = data["data"]["viewer"]["repositories"]["nodes"]
        if "organization" in data["data"]:
            repo_nodes += data["data"]["organization"]["repositories"]["nodes"]
        for repo in repo_nodes:
            if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
                repos.append(repo)
                repo_names.add(repo["name"])

                latest_release_node = [
                    node
                    for node in repo["releases"]["nodes"]
                    if not node["isDraft"] and not node["isPrerelease"]
                ][-1]
                releases.append(
                    {
                        "repo": repo["name"],
                        "repo_url": repo["url"],
                        "description": repo["description"],
                        "release": latest_release_node["name"]
                        .replace(repo["name"], "")
                        .strip(),
                        "published_at": latest_release_node["publishedAt"],
                        "published_day": latest_release_node["publishedAt"].split("T")[
                            0
                        ],
                        "url": latest_release_node["url"],
                        "total_releases": repo["releases"]["totalCount"],
                    }
                )
        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return releases


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


releases = fetch_releases(TOKEN)
releases.sort(key=lambda r: r["published_at"], reverse=True)
print(releases)
md = "\n\n".join(
    [
        "[{repo} {release}]({url}) - {published_day}".format(**release)
        for release in releases[:8]
    ]
)

with open("README.md", "r") as readme_file:
    README = readme_file.read()

rewritten = replace_chunk(README, "recent_releases", md)

with open("README.md", "w") as readme_file:
    readme_file.write(rewritten)
