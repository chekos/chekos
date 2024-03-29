"""Updates README file with my latest TILs and blog entries."""

import feedparser

def fetch_blog_entries(feed_url):
    entries = feedparser.parse(feed_url)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]

TIL_feed = "https://til.soyserg.io/feed"
blog_feed = "https://chekos.dev/feed"
tils_entries = fetch_blog_entries(TIL_feed)[:5]
tils_md = "<li>".join(
        ["[{title}]({url}) - {published}".format(**entry) for entry in tils_entries]
    )

blog_entries = fetch_blog_entries(blog_feed)[:5]
blog_md = "<li>".join(
        ["[{title}]({url}) - {published}".format(**entry) for entry in blog_entries]
)

table = f"""
|  @ [chekos.dev](https://chekos.dev/)   |   @ [TIL.soyserg.io](https://til.soyserg.io/) |
|:---------------------------------------|:----------------------------------------------|
|         <ul><li>{blog_md}</ul>         |             <ul><li>{tils_md}</ul>            |
"""

with open("README.md", "r") as readme_file:
    README = readme_file.read()

split_readme = README.split("<!-- most_recent_entries -->")
split_readme[1] = f"<!-- most_recent_entries -->\n{table}\n<!-- most_recent_entries -->"
with open("README.md", "w") as file:
    file.write("".join(split_readme))