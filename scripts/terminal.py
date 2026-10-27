"""The README intro as a Ghostty window: assets/terminal-{dark,light}.svg.

Colors come from my Ghostty themes (TokyoNight Moon Blue at night, TokyoNight Day
by day) and the neon-border shader; the prompt mimics my powerlevel10k setup.
Commands type themselves out once, then the cursor blinks on an empty prompt.
"""

from xml.sax.saxutils import escape

THEMES = {
    "dark": dict(bg="#222436", bar="#1e2030", fg="#c8d3f5", dim="#7b9cc9", dir="#82aaff", git="#c3e88d",
                 prompt="#c3e88d", cursor="#dfe6ff", neon=("#dfe6ff", "#5c6b9e", "#2a3358")),
    "light": dict(bg="#e1e2e7", bar="#d0d5e3", fg="#3760bf", dim="#6172b0", dir="#2e7de9", git="#587539",
                  prompt="#587539", cursor="#3760bf", neon=("#6172b0", "#99a7df", "#3760bf")),
}
TRAFFIC = ("#ff5f57", "#febc2e", "#28c840")

SESSION = [
    ("whoami", "you li · cs @ nyu courant"),
    ("cat interests.txt", "ml systems · accelerator kernels · agents · basketball · league of legends"),
    ("cat fun_fact.txt", "the whale is a carp in disguise. 🐟"),
]

FONT = 15
CW = FONT * 0.6  # monospace advance; every run is pinned to this with textLength
LH = 22
PAD_X, BAR_H, PAD_TOP = 26, 38, 18
W = 760
TYPE_S = 0.06  # seconds per typed character
PAUSE = 0.45  # between a command finishing and the next prompt


def lines():
    """(kind, segments, start time) for every visual line; segments are (text, color key)."""
    out, t = [], 0.5
    out.append(("show", [("~/you-li", "dir"), ("  main", "git")], 0.0))
    for cmd, result in SESSION:
        out.append(("type", [("❯ ", "prompt"), (cmd, "fg")], t))
        t += len(cmd) * TYPE_S + 0.25
        out.append(("show", [(result, "dim")], t))
        out.append(("show", [], t))
        t += PAUSE
    out.append(("show", [("❯ ", "prompt")], t))
    return out, t


def render(theme):
    p = THEMES[theme]
    rows, done = lines()
    h = BAR_H + PAD_TOP + len(rows) * LH + 12
    parts, css = [], []

    # neon border: a rotating gradient stroke plus a blurred copy for the glow
    a, b, c = p["neon"]
    parts.append(
        f'<defs><linearGradient id="neon" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="0.5" stop-color="{b}"/><stop offset="1" stop-color="{c}"/>'
        f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="8s" repeatCount="indefinite"/>'
        f'</linearGradient><filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="4"/></filter></defs>'
    )
    parts.append(f'<rect x="6" y="6" width="{W - 12}" height="{h - 12}" rx="12" fill="none" stroke="url(#neon)" stroke-width="3" filter="url(#glow)" opacity="0.8"/>')
    parts.append(f'<rect x="6" y="6" width="{W - 12}" height="{h - 12}" rx="12" fill="{p["bg"]}" stroke="url(#neon)" stroke-width="1.5"/>')
    parts.append(f'<path d="M6 {6 + BAR_H} V18 a12 12 0 0 1 12 -12 H{W - 18} a12 12 0 0 1 12 12 V{6 + BAR_H} Z" fill="{p["bar"]}"/>')
    for i, color in enumerate(TRAFFIC):
        parts.append(f'<circle cx="{28 + i * 20}" cy="{6 + BAR_H / 2}" r="6" fill="{color}"/>')
    parts.append(f'<text x="{W / 2}" y="{6 + BAR_H / 2 + 5}" text-anchor="middle" class="t" fill="{p["dim"]}">you-li — zsh</text>')

    y0 = 6 + BAR_H + PAD_TOP
    for i, (kind, segs, start) in enumerate(rows):
        y = y0 + i * LH
        x = PAD_X
        runs = []
        for text, key in segs:
            n = len(text)
            runs.append(f'<text x="{x:g}" y="{y}" class="t" fill="{p[key]}" textLength="{n * CW:g}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
            x += n * CW
        body = "".join(runs)
        if kind == "type":
            # the prompt glyph appears at once; the command is revealed one character per step
            n = len(segs[1][0])
            width = (2 + n) * CW
            parts.append(f'<clipPath id="c{i}"><rect class="r{i}" x="{PAD_X}" y="{y - LH + 6}" width="{width:g}" height="{LH}"/></clipPath>')
            parts.append(f'<g class="l{i}" clip-path="url(#c{i})">{body}</g>')
            css.append(f".r{i} {{ transform-box: fill-box; transform-origin: left; transform: scaleX({2 / (2 + n):.4f}); "
                       f"animation: type {n * TYPE_S:.2f}s steps({n}) {start:.2f}s forwards; }}")
        else:
            parts.append(f'<g class="l{i}">{body}</g>')
        css.append(f".l{i} {{ opacity: 0; animation: show 0.01s {start:.2f}s forwards; }}")
    cy = y0 + (len(rows) - 1) * LH
    parts.append(f'<rect class="cursor" x="{PAD_X + 2 * CW:g}" y="{cy - FONT + 2}" width="{CW:g}" height="{FONT + 3}" fill="{p["cursor"]}"/>')

    style = "\n".join([
        f".t {{ font-family: 'Maple Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: {FONT}px; white-space: pre; }}",
        "@keyframes show { to { opacity: 1; } }",
        "@keyframes type { to { transform: scaleX(1); } }",
        f".cursor {{ opacity: 0; animation: blink 1.1s steps(1) {done:.2f}s infinite; }}",
        "@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } }",
        *css,
    ])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
        f'aria-label="whoami: you li, cs at nyu courant. interests: ml systems, accelerator kernels, agents, '
        f'basketball, league of legends. fun fact: the whale is a carp in disguise.">'
        f"<style>{style}</style>{''.join(parts)}</svg>\n"
    )
