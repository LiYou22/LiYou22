"""Generate the profile banner (assets/banner-{dark,light}.svg).

The Chrome offline dino game, underwater and in blue: the seabed scrolls by
like the dino's ground, and the whale swims through, rising over tall kelp and
dipping under jellyfish, trailing bubbles. The scoreboard is real: fish fed by
visitors on the left; on the right HI is my best day and the score rolls up to
this year's contributions. The dark theme is the game's night mode, with a moon.
"""

from pixel import FISH, FONT, THEMES, WHALE, bitmap, mono_whale, rect, svg, text, text_width

W, H = 900, 180
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


COUNT_UP_S = 3
CLOUD_X = (150, W - 350)


def odometer(p, x, y, s, value, prefix):
    """Five digits that roll up from 00000 to `value` once, then hold.

    Each digit is a 0-9 strip scrolled under a clip with steps(10); a fractional
    iteration count leaves every strip parked on its final digit.
    """
    slot = 8 * s
    parts, css = [], []
    for k in range(5):
        dx = x + k * 6 * s
        digits = []
        for d in range(10):
            digits += bitmap(FONT[str(d)], dx, y + d * slot, s, p["fg"])
        cycles = value / 10 ** (5 - k)
        if cycles:
            css.append(f".{prefix}{k} {{ animation: odo {COUNT_UP_S / cycles:.4f}s steps(10) {cycles + 1e-4:.4f} forwards; }}")
        parts.append(
            f'<clipPath id="{prefix}c{k}"><rect x="{dx}" y="{y}" width="{5 * s}" height="{7 * s}"/></clipPath>'
            f'<g clip-path="url(#{prefix}c{k})"><g class="{prefix}{k}">{"".join(digits)}</g></g>'
        )
    return "".join(parts), "\n".join(css)


def scoreboard(p, stats, s=3):
    """Top left: fish fed so far. Top right: HI = best day, then the year's contributions."""
    parts = bitmap(FISH, 20, 14, s, p["fg"])
    parts += text(f"X{min(stats['fed'], 999):03d}", 20 + 10 * s + 6, 12, s, p["muted"])
    x = W - 20 - text_width("HI 00000 00000", s)
    parts += text(f"HI {min(stats['best'], 99999):05d}", x, 12, s, p["muted"])
    total, css = odometer(p, x + 9 * 6 * s, 12, s, min(stats["total"], 99999), "t")
    css += f"\n@keyframes odo {{ to {{ transform: translateY(-{10 * 8 * s}px); }} }}"
    return "".join(parts) + total, css


def render(theme, stats):
    """stats: best (max contributions in a day), total (contributions this year), fed (fish fed)."""
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
    clouds = []
    for dx in (0, W):
        clouds += bitmap(CLOUD, 200 + dx, 10, 2, p["soft"]) + bitmap(CLOUD, 470 + dx, 22, 2, p["soft"])
    # clouds drift only through the middle of the sky so they never cross the scoreboards
    sky = [f'<clipPath id="sky"><rect x="{CLOUD_X[0]}" y="0" width="{CLOUD_X[1] - CLOUD_X[0]}" height="{SURFACE}"/></clipPath>'
           f'<g clip-path="url(#sky)"><g class="clouds">{"".join(clouds)}</g></g>']
    if theme == "dark":
        sky += bitmap(MOON, 330, 10, 3, p["fg"])
    board, board_css = scoreboard(p, stats)

    parts = [
        rect(0, SURFACE, W, SEABED - SURFACE, p["water"]),
        *sky, board, surface(p), strip(p),
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
        board_css,
    ])
    return svg(W, H, "A pixel whale swimming through the Chrome dino game", style, parts)
