"""Shared pixel-art pieces for the profile SVGs: bitmap font, whale sprite, blue palettes.

Glyphs and sprites are drawn as <rect>s because GitHub serves README images through
<img>, where SVGs cannot load web fonts.
"""

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "~": [".....", ".....", ".#...", "#.#.#", "...#.", ".....", "....."],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
}

# Facing left, tail curled up on the right. D outline, B body, L belly,
# E eye, W glint, P cheek, K mouth.
WHALE = [
    "....DDDDDDDD............",
    "..DDBBBBBBBBDD.......DD.",
    ".DBBBBBBBBBBBBDD....DBBD",
    ".DBBBBBBBBBBBBBBD..DBBD.",
    "DBBWEBBBBBBBBBBBBDDBBD..",
    "DBBEEBBBBBBBBBBBBBBBD...",
    "DBPBBBBBBBBBBBBBBBBD....",
    "DBBBKKBBBBBBBBBBBBD.....",
    "DLLLLLLBBBBBBBBBBD......",
    ".DLLLLLLLLLLBBBDD.......",
    "..DDLLLLLLLLLDD.........",
    "....DDDDDDDDD...........",
]

# One blue per theme in the Chrome dino game's single-color style (Tokyo Night blues).
THEMES = {
    "light": dict(fg="#2e7de9", soft="#b6c6f0", muted="#7aa2f7", water="#f3f7fe", bubble="#7aa2f7"),
    "dark": dict(fg="#7aa2f7", soft="#3d59a1", muted="#565f89", water="#111a2e", bubble="#7dcfff"),
}


FISH = [
    "..###...#",
    ".#####.##",
    "#.######.",
    ".#####.##",
    "..###...#",
]


def text(s, x, y, scale, fill):
    out = []
    for i, ch in enumerate(s):
        out += bitmap(FONT[ch], x + i * 6 * scale, y, scale, fill)
    return out


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def mono_whale(tail_down):
    """WHALE as a right-facing silhouette; eye and mouth become holes."""
    rows = [list(r) for r in WHALE]
    if tail_down:
        tail = [(r, c) for r in range(len(rows)) for c in range(19, len(rows[0])) if rows[r][c] != "."]
        moved = {(r, c): rows[r][c] for r, c in tail}
        for r, c in tail:
            rows[r][c] = "."
        for (r, c), k in moved.items():
            rows[min(r + 2, len(rows) - 1)][c] = k
    return ["".join("." if k in ".EWK" else "#" for k in reversed(row)) for row in rows]


def rect(x, y, w, h, fill):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}"/>'


def bitmap(rows, x, y, s, fill):
    """Draw '#' cells of a bitmap, merging horizontal runs into one rect."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == "#":
                start = c
                while c < len(row) and row[c] == "#":
                    c += 1
                out.append(rect(x + start * s, y + r * s, (c - start) * s, s, fill))
            else:
                c += 1
    return out


def svg(w, h, label, style, parts):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}">'
        f"<style>{style}</style>{''.join(parts)}</svg>\n"
    )
