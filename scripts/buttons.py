"""README footer buttons in the NES.css style: notched border, flat fill, bottom-right bevel.

Text uses the 8x8 Press Start 2P glyphs from font8.py.
"""

from font8 import FONT8
from pixel import bitmap, rect, svg

S = 3  # glyph pixel size
U = 4  # border / bevel thickness
PAD_X, PAD_Y = 22, 16
H = 7 * S + 2 * PAD_Y

LINK = [
    "...#####",
    ".....###",
    "....##.#",
    "...##..#",
    "..##....",
    ".##.....",
    "##......",
]

# NES.css default button colors, per theme
STYLES = {
    "light": dict(fill="#ffffff", bevel="#c0c4d6", border="#1a1b26", ink="#1a1b26"),
    "dark": dict(fill="#1a1b26", bevel="#0f1018", border="#c0caf5", ink="#c0caf5"),
}


def label(s, x, y, fill):
    out = []
    for i, ch in enumerate(s):
        out += bitmap(FONT8[ch], x + i * 8 * S, y, S, fill)
    return out


def button(theme, text, icon):
    c = STYLES[theme]
    icon_w = len(icon[0]) * S
    w = PAD_X + icon_w + 14 + len(text) * 8 * S - S + PAD_X
    parts = [
        rect(U, 0, w - 2 * U, H, c["border"]), rect(0, U, w, H - 2 * U, c["border"]),
        rect(U, U, w - 2 * U, H - 2 * U, c["fill"]),
        rect(U, H - 2 * U, w - 2 * U, U, c["bevel"]), rect(w - 2 * U, U, U, H - 2 * U, c["bevel"]),
    ]
    parts += bitmap(icon, PAD_X, (H - U - len(icon) * S) // 2, S, c["ink"])
    parts += label(text, PAD_X + icon_w + 14, PAD_Y - U // 2, c["ink"])
    return svg(w, H, text.title(), "", parts)


def render_all():
    """{filename stem: svg} for every theme."""
    out = {}
    for t in STYLES:
        out[f"links-{t}"] = button(t, "LINKEDIN", LINK)
    return out
