"""Render the README banner into assets/: python3 scripts/render.py"""

from pathlib import Path

import banner
from pixel import THEMES

out = Path(__file__).resolve().parent.parent / "assets"
out.mkdir(exist_ok=True)
for t in THEMES:
    (out / f"banner-{t}.svg").write_text(banner.render(t))
