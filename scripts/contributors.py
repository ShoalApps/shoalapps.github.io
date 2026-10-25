"""Writes contributors.json: everyone who has contributed to a public Tintloom repository.

Run by GitHub Actions with its token, so the website never calls the GitHub API from
visitors' browsers (which fails on shared or VPN addresses once the anonymous limit is used).
"""
import json
import os
import urllib.request

ORG = "Tintloom"
# The maintainer's alternate accounts: their work is credited under calamityCocoa.
HIDDEN = {"aaronateataco2", "calamitycocoa2"}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


people = {}
for repo in get(f"https://api.github.com/orgs/{ORG}/repos?type=public&per_page=100"):
    for c in get(f"https://api.github.com/repos/{ORG}/{repo['name']}/contributors?per_page=100"):
        login = c["login"]
        if c.get("type") != "User" or login.lower() in HIDDEN or login.endswith("[bot]"):
            continue
        p = people.setdefault(login, {"login": login, "avatar": c["avatar_url"], "url": c["html_url"], "contributions": 0})
        p["contributions"] += c["contributions"]

# The maintainer always appears, even before their account has commits of its own.
people.setdefault("calamityCocoa", {
    "login": "calamityCocoa",
    "avatar": "https://avatars.githubusercontent.com/calamityCocoa",
    "url": "https://github.com/calamityCocoa",
    "contributions": 0,
})

ranked = sorted(people.values(), key=lambda p: (-p["contributions"], p["login"].lower()))
with open("contributors.json", "w") as f:
    json.dump(ranked, f, indent=2)
    f.write("\n")
print(f"{len(ranked)} contributors")
