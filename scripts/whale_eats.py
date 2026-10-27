"""Render the whale eating my contribution graph: OUT_DIR/whale-eats-{dark,light}.svg.

Usage: whale_eats.py OUT_DIR [CALENDAR_JSON]

Without CALENDAR_JSON the calendar is fetched from the GitHub GraphQL API for
$GITHUB_USER using $GITHUB_TOKEN. Drawn in the banner's single-blue dino style:
the whale swims the grid row by row, alternating direction, and every non-empty
day shrinks back to an empty dot as its mouth passes; the grid regrows at the
end of each loop.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

from pixel import THEMES, WHALE, bitmap, mono_whale, rect, svg

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { weekday contributionLevel } } }
    }
  }
}
"""
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
OPACITY = [0, 0.35, 0.55, 0.8, 1]

W = 900
SURFACE, TOP = 10, 26
CELL, SIZE, DOT = 14, 10, 4
SEABED = TOP + 7 * CELL + 12
H = SEABED + 22
S = 2
WHALE_W, WHALE_H = len(WHALE[0]) * S, len(WHALE) * S
SPEED = CELL / 0.08  # px per second
TURN = 0.35
HOLD = 1.5
REGROW = 0.6


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "whale-eats"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def grid(data):
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    cells = [(i, d["weekday"], LEVELS.index(d["contributionLevel"]))
             for i, week in enumerate(weeks) for d in week["contributionDays"]]
    return len(weeks), cells


def timeline(n_weeks, cells, x0):
    """Whale keyframes (t, x, y, facing_left) and the time each non-empty cell is eaten."""
    left_edge, right_edge = x0 - 16, x0 + n_weeks * CELL + 16
    t, x = 0.0, W + 20
    keys, eaten = [], {}
    for r in range(7):
        y = TOP + r * CELL + SIZE / 2 - WHALE_H / 2
        facing_left = r % 2 == 0
        if r == 0:
            keys.append((t, x, y, facing_left))
        else:
            keys.append((t, x, keys[-1][2], facing_left))
            t += TURN
            keys.append((t, x, y, facing_left))
        front = x if facing_left else x + WHALE_W
        end = (-WHALE_W - 30 if r == 6 else left_edge) if facing_left else right_edge
        for i, row, level in cells:
            if row == r and level:
                eaten[(i, row)] = t + abs(x0 + i * CELL + SIZE / 2 - front) / SPEED
        t += abs(end - front) / SPEED
        x = end if facing_left else end - WHALE_W
        keys.append((t, x, y, facing_left))
    return keys, eaten, t + HOLD + REGROW


def pct(t, total):
    return f"{100 * t / total:.3f}%"


def render(theme, n_weeks, cells):
    p = THEMES[theme]
    x0 = (W - n_weeks * CELL) // 2
    keys, eaten, total = timeline(n_weeks, cells, x0)
    regrow_at = pct(total - REGROW, total)

    parts = [rect(0, SURFACE, W, SEABED - SURFACE, p["water"])]
    parts += [rect(x, SURFACE, 16, 2, p["fg"]) for x in range(0, W, 24)]
    parts.append(rect(0, SEABED, W, 2, p["fg"]))
    parts += [rect(x, SEABED + 6 + (i * 7) % 12, 4 + (i * 5) % 9, 2, p["soft"])
              for i, x in enumerate(range(13, W, 37))]

    css = []
    for k, (i, row, level) in enumerate(cells):
        x, y = x0 + i * CELL, TOP + row * CELL
        parts.append(rect(x + (SIZE - DOT) / 2, y + (SIZE - DOT) / 2, DOT, DOT, p["soft"]))
        if not level:
            continue
        cell = f'<rect x="{x}" y="{y}" width="{SIZE}" height="{SIZE}" fill="{p["fg"]}" opacity="{OPACITY[level]}"'
        if (i, row) in eaten:
            at = eaten[(i, row)]
            css.append(f"@keyframes e{k} {{ 0%, {pct(at, total)} {{ opacity: 1; }} "
                       f"{pct(at + 0.02, total)}, {regrow_at} {{ opacity: 0; }} 100% {{ opacity: 1; }} }}")
            cell = f'<g style="animation: e{k} {total:.2f}s linear infinite">{cell}/></g>'
        else:
            cell += "/>"
        parts.append(cell)

    swim = "".join(
        f'<g class="alt a{i}">{"".join(bitmap(mono_whale(i == 1), 0, 0, S, p["fg"]))}</g>' for i in range(2)
    )
    parts.append(f'<clipPath id="water"><rect x="0" y="{SURFACE}" width="{W}" height="{SEABED - SURFACE}"/></clipPath>'
                 f'<g clip-path="url(#water)"><g class="swim"><g class="turn">{swim}</g></g></g>')

    move = " ".join(f"{pct(tk, total)} {{ transform: translate({x:.1f}px, {y:.1f}px); }}" for tk, x, y, _ in keys)
    move += f" 100% {{ transform: translate({keys[-1][1]:.1f}px, {keys[-1][2]:.1f}px); }}"
    # the silhouette faces right, so swimming left means mirroring it
    turn = " ".join(f"{pct(tk, total)} {{ transform: scaleX({-1 if left else 1}); }}" for tk, _, _, left in keys)
    turn += f" 100% {{ transform: scaleX({-1 if keys[-1][3] else 1}); }}"
    style = "\n".join([
        f".swim {{ animation: swim {total:.2f}s linear infinite; }}",
        f".turn {{ transform-box: fill-box; transform-origin: center; animation: turn {total:.2f}s steps(1) infinite; }}",
        f"@keyframes swim {{ {move} }}",
        f"@keyframes turn {{ {turn} }}",
        ".alt { animation: alt 0.6s steps(1) infinite; }",
        ".a1 { animation-delay: -0.3s; }",
        "@keyframes alt { 0% { opacity: 1; } 50% { opacity: 0; } }",
        *css,
    ])
    return svg(W, H, "A whale eating my GitHub contribution graph", style, parts)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    if len(sys.argv) > 2:
        data = json.loads(Path(sys.argv[2]).read_text())
    else:
        data = fetch(os.environ["GITHUB_USER"], os.environ["GITHUB_TOKEN"])
    n_weeks, cells = grid(data)
    out.mkdir(parents=True, exist_ok=True)
    for t in THEMES:
        (out / f"whale-eats-{t}.svg").write_text(render(t, n_weeks, cells))
