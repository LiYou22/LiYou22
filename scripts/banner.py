"""Generate the profile banner (assets/banner-{dark,light}.svg).

The Chrome offline dino game, underwater and in blue: the seabed scrolls by
like the dino's ground, and the whale swims through, rising over tall kelp and
dipping under jellyfish, trailing bubbles. A one-line intro sits in the sky in
the Press Start 2P pixel font. The dark theme is the game's night mode, with a
moon above the surface.
"""

from font8 import FONT8
from pixel import THEMES, WHALE, bitmap, mono_whale, rect, svg

W, H = 900, 180
TITLE = "CS @ NYU COURANT"
TITLE_S = 2  # title pixel size
PX = 4  # sprite pixel size
SURFACE, SEABED = 44, 160
SPEED = 180  # px per second; the seabed strip repeats every W px
LOOP = W / SPEED

WHALE_X = 90
CRUISE_Y = 84  # top of the whale while nothing is in the way

ROCK = [
    "..##..",
    ".####.",
    "######",
    "######",
]
KELP = [
    ["..#.", ".#..", ".#..", "..#.", "..#.", ".#..", ".#..", "..#.", "..#.", ".#..", "##.#", ".###"],
    [".#..", "..#.", "..#.", ".#..", ".#..", "..#.", "..#.", ".#..", ".#..", "..#.", "#.##", "###."],
]
JELLY = [
    ["..####..", ".######.", "########", "#.#..#.#", ".#.##.#.", "#..#..#."],
    ["..####..", ".######.", "########", ".#.##.#.", "#.#..#.#", ".#.#..#."],
]
CLOUD = [
    ".....####.....",
    "...##....##...",
    ".###........#.",
    "#............#",
    "##############",
]
MOON = ["..###", ".##..", "##...", "##...", "##...", ".##..", "..###"]

# (x within the repeating strip, sprite frames, top y, how the whale avoids it)
OBSTACLES = [
    (250, [ROCK], SEABED - len(ROCK) * PX, None),
    (480, KELP, SEABED - len(KELP[0]) * PX, ("over", 56)),
    (820, JELLY, SURFACE + 4, ("under", 100)),
]


def strip(p):
    """Seabed line, sand texture and obstacles for one W-wide tile, drawn twice for wrapping."""
    parts = []
    for dx in (0, W):
        parts.append(rect(dx, SEABED, W, 2, p["fg"]))
        for i, x in enumerate(range(13, W, 37)):
            parts.append(rect(dx + x, SEABED + 6 + (i * 7) % 12, 4 + (i * 5) % 9, 2, p["soft"]))
        for x, frames, top, _ in OBSTACLES:
            for i, frame in enumerate(frames):
                cls = f' class="alt a{i}"' if len(frames) > 1 else ""
                parts.append(f'<g{cls}>{"".join(bitmap(frame, dx + x, top, PX, p["fg"]))}</g>')
    return f'<g class="seabed">{"".join(parts)}</g>'


def surface(p):
    parts = []
    for dx in (0, W):
        for x in range(0, W, 24):
            parts.append(rect(dx + x, SURFACE + (2 if (x // 24) % 2 else 0), 16, 2, p["fg"]))
    return f'<g class="surface">{"".join(parts)}</g>'


def swim_css():
    """Keyframes for the whale's depth: cruise, then ease over or under each obstacle in turn."""
    whale_w = len(WHALE[0]) * PX
    keys = [(0.0, CRUISE_Y)]
    for x, frames, _, avoid in OBSTACLES:
        if avoid is None:
            continue
        enter = (x - (WHALE_X + whale_w)) / SPEED
        leave = (x + len(frames[0][0]) * PX - WHALE_X) / SPEED
        keys += [(enter - 0.5, CRUISE_Y), (enter - 0.1, avoid[1]), (leave + 0.1, avoid[1]), (leave + 0.5, CRUISE_Y)]
    keys.append((LOOP, CRUISE_Y))
    body = " ".join(f"{100 * t / LOOP:.2f}% {{ transform: translateY({y - CRUISE_Y}px); }}" for t, y in keys)
    return f"@keyframes depth {{ {body} }}"


def render(theme):
    p = THEMES[theme]
    swim = "".join(
        f'<g class="alt a{i}">{"".join(bitmap(mono_whale(i == 1), WHALE_X, CRUISE_Y, PX, p["fg"]))}</g>'
        for i in range(2)
    )
    head_x = WHALE_X + len(WHALE[0]) * PX - 14
    bubbles = "".join(
        f'<g class="bubble" style="animation-delay:{i * 0.6:.1f}s">{rect(head_x + i * 5, CRUISE_Y + 6, 4, 4, p["bubble"])}</g>'
        for i in range(3)
    )
    title = []
    for i, ch in enumerate(TITLE):
        title += bitmap(FONT8[ch], 20 + i * 8 * TITLE_S, 14, TITLE_S, p["fg"])
    sky_x = 20 + len(TITLE) * 8 * TITLE_S + 24  # clouds and moon stay right of the title
    clouds = []
    for dx in (0, W):
        clouds += bitmap(CLOUD, sky_x + 60 + dx, 10, 2, p["soft"]) + bitmap(CLOUD, sky_x + 300 + dx, 22, 2, p["soft"])
    sky = [
        *title,
        f'<clipPath id="sky"><rect x="{sky_x}" y="0" width="{W - sky_x}" height="{SURFACE}"/></clipPath>'
        f'<g clip-path="url(#sky)"><g class="clouds">{"".join(clouds)}</g></g>',
    ]
    if theme == "dark":
        sky += bitmap(MOON, W - 60, 10, 3, p["fg"])

    parts = [
        rect(0, SURFACE, W, SEABED - SURFACE, p["water"]),
        *sky, surface(p), strip(p),
        f'<g class="depth"><g class="bob">{swim}{bubbles}</g></g>',
    ]
    style = "\n".join([
        f".seabed {{ animation: scroll {LOOP:g}s linear infinite; }}",
        f".surface {{ animation: scroll {2 * LOOP:g}s linear infinite; }}",
        f".clouds {{ animation: scroll {12 * LOOP:g}s linear infinite; }}",
        f"@keyframes scroll {{ to {{ transform: translateX(-{W}px); }} }}",
        f".depth {{ animation: depth {LOOP:g}s ease-in-out infinite; }}",
        swim_css(),
        ".bob { animation: bob 1.6s ease-in-out infinite alternate; }",
        "@keyframes bob { from { transform: translateY(-2px); } to { transform: translateY(3px); } }",
        ".alt { animation: alt 0.6s steps(1) infinite; }",
        ".a1 { animation-delay: -0.3s; }",
        "@keyframes alt { 0% { opacity: 1; } 50% { opacity: 0; } }",
        ".bubble { opacity: 0; animation: bubble 1.8s linear infinite; }",
        "@keyframes bubble { 0% { opacity: 1; transform: translate(0, 0); } 100% { opacity: 0; transform: translate(10px, -34px); } }",
    ])
    return svg(W, H, f"{TITLE.lower()}: a pixel whale swimming through the Chrome dino game", style, parts)
