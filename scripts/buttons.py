"""Pixel buttons and link text for the README footer, in the banner's blue."""

from pixel import FISH, THEMES, bitmap, rect, svg, text, text_width

S = 3  # font scale
PAD = 14
H = 7 * S + 2 * PAD

PLAY = ["#...", "##..", "###.", "####", "###.", "##..", "#..."]


def button(theme, label, icon):
    """A notched pixel button: border, water-colored fill, icon, label."""
    p = THEMES[theme]
    icon_w = len(icon[0]) * S
    w = PAD + icon_w + 10 + text_width(label, S) + PAD
    parts = [
        rect(3, 0, w - 6, H, p["fg"]), rect(0, 3, w, H - 6, p["fg"]),
        rect(6, 3, w - 12, H - 6, p["water"]), rect(3, 6, w - 6, H - 12, p["water"]),
    ]
    parts += bitmap(icon, PAD, (H - len(icon) * S) // 2, S, p["fg"])
    parts += text(label, PAD + icon_w + 10, PAD, S, p["fg"])
    return svg(w, H, label.title(), "", parts)


def links(theme):
    """'LINKS: LINKEDIN' with the link text underlined."""
    p = THEMES[theme]
    lead = "LINKS:"
    x = text_width(lead, S) + 4 * S
    w = x + text_width("LINKEDIN", S)
    parts = text(lead, 0, 4, S, p["muted"]) + text("LINKEDIN", x, 4, S, p["fg"])
    parts.append(rect(x, 4 + 8 * S, text_width("LINKEDIN", S), S, p["fg"]))
    return svg(w, 9 * S + 8, "Links: LinkedIn", "", parts)


def render_all():
    """{filename stem: svg} for every theme."""
    out = {}
    for t in THEMES:
        out[f"play-{t}"] = button(t, "PLAY", PLAY)
        out[f"feed-{t}"] = button(t, "FEED THE WHALE", FISH)
        out[f"links-{t}"] = links(t)
    return out
