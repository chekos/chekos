"""Updates README file with the 5 last updated repos in my account."""

import pandas as pd
import requests as r
import os

TOKEN = os.environ.get("PAT", "")
GITHUB_API_URL = "https://api.github.com/"


headers = {
    "Authorization": f"token {TOKEN}",
}

repo_params = {
    "per_page": 100,
    "page": 1,
}

dfs = []
for page_n in range(1,3):
    repo_params['page'] = page_n
    response = r.get(GITHUB_API_URL + "user/repos", headers = headers, params = repo_params)
    if response.status_code == 200:
        dfs.append(pd.DataFrame(response.json()))

working_df = pd.concat(dfs)
owner_df = working_df['owner'].apply(pd.Series)
owner_df.columns = [f"owner_{col}" for col in owner_df.columns]
working_df = pd.concat([working_df, owner_df], axis = 1, )

my_logins = [
    "chekos",
    "tacosdedatos",
    "we-are-alluma",
    "cimarron-io",
    "vivaladataviz",
    "socialtechus",
]
mask_login = working_df['owner_login'].isin(my_logins)
my_repos = working_df[mask_login].copy()

mask_only_public = my_repos['private'] == False
mask_not_this_repo = my_repos['full_name'] != "chekos/chekos"
most_recent_repos = my_repos[mask_only_public & mask_not_this_repo].sort_values(by = 'updated_at', ascending = False).head(10).copy()

voi = [
    "full_name",
    "html_url",
    "description",
    "homepage"
]

to_publish = most_recent_repos[voi].copy()

to_publish['repo'] = "["+ to_publish['full_name'] + "](" + to_publish['html_url'] + ")"
to_publish.reset_index(drop = True, inplace = True)

with open("most_recent_repos.md", "w") as file:
    to_publish[["repo", "description", "homepage"]].head().to_markdown(file)

with open("README.md", "r") as readme_file:
    README = readme_file.read()

table = to_publish[["repo", "description", "homepage"]].head().to_markdown()
split_readme = README.split("<!-- most_recent_repos -->")
split_readme[1] = f"<!-- most_recent_repos -->\n{table}\n<!-- most_recent_repos -->"
with open("README.md", "w") as file:
    file.write("".join(split_readme))