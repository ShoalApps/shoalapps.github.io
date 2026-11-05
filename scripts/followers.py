"""Writes followers.json: everyone following ShoalApps on GitHub, oldest first as GitHub lists them.

Each is drawn as a sea urchin on the website's sea floor. Run by GitHub Actions with its token,
so the website never calls the GitHub API from visitors' browsers.
"""
import json
import os
import urllib.request

ORG = "ShoalApps"
# The maintainer's alternate accounts aren't followers to show off.
HIDDEN = {"aaronateataco2", "calamitycocoa2"}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


followers = []
page = 1
while True:
    batch = get(f"https://api.github.com/users/{ORG}/followers?per_page=100&page={page}")
    followers += [{"login": f["login"], "avatar": f["avatar_url"], "url": f["html_url"]}
                  for f in batch if f["login"].lower() not in HIDDEN and not f["login"].endswith("[bot]")]
    if len(batch) < 100:
        break
    page += 1

with open("followers.json", "w") as out:
    json.dump(followers, out, indent=2)
    out.write("\n")
print(f"{len(followers)} followers")
