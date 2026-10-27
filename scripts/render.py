"""Render every README image into OUT_DIR: render.py OUT_DIR [CALENDAR_JSON].

Without CALENDAR_JSON the contribution calendar is fetched from the GitHub
GraphQL API for $GITHUB_USER using $GITHUB_TOKEN. The fish count comes from
data/feed.json.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

import banner
import buttons
from pixel import THEMES

ROOT = Path(__file__).resolve().parent.parent
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount } } }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "whale-banner"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def stats(data):
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    best = max(d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"])
    fed = json.loads((ROOT / "data" / "feed.json").read_text())["count"]
    return {"best": best, "total": cal["totalContributions"], "fed": fed}


if __name__ == "__main__":
    out = Path(sys.argv[1])
    if len(sys.argv) > 2:
        data = json.loads(Path(sys.argv[2]).read_text())
    else:
        data = fetch(os.environ["GITHUB_USER"], os.environ["GITHUB_TOKEN"])
    s = stats(data)
    out.mkdir(parents=True, exist_ok=True)
    for t in THEMES:
        (out / f"banner-{t}.svg").write_text(banner.render(t, s))
    for stem, doc in buttons.render_all().items():
        (out / f"{stem}.svg").write_text(doc)
    print(s)
