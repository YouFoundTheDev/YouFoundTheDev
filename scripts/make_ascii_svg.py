#!/usr/bin/env python3
"""Turn source-prepped.png into a monochrome, self-typing ASCII SVG.

Each row is clipped and wiped left to right, staggered top to bottom, with a
small cursor riding the wipe edge. The animation plays once and freezes.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright -> dark
COLS = 100
CHAR_W = 4.3          # px per monospace cell at FONT_SIZE
FONT_SIZE = 7.4
LINE_H = 7.9
PAD = 10
FG = "#8b949e"
BG = "#0d1117"
CURSOR = "#39d353"


def main() -> None:
    src = Path("source-prepped.png")
    if not src.exists():
        raise SystemExit("run scripts/prep_photo.py first")

    img = Image.open(src).convert("L")
    w, h = img.size
    rows = max(12, int(COLS * (h / w) * 0.5))
    img = img.resize((COLS, rows), Image.LANCZOS)

    px = np.asarray(img).astype(np.float32)
    # Stretch the tones the face actually uses, then map bright pixels to
    # sparse glyphs (space) and dark pixels to dense ones.
    lo, hi = np.percentile(px, [4, 96])
    if hi > lo:
        px = np.clip((px - lo) / (hi - lo), 0.0, 1.0) * 255.0
    brightness = (px / 255.0) ** 1.05
    idx = np.clip(((1.0 - brightness) * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)

    width = COLS * CHAR_W + PAD * 2
    height = rows * LINE_H + PAD * 2

    clips = []
    groups = []
    for r in range(rows):
        y = PAD + r * LINE_H
        text = "".join(RAMP[i] for i in idx[r])
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        begin = 0.06 * r
        dur = 0.32
        clips.append(
            f'<clipPath id="r{r}"><rect x="{PAD}" y="{y - LINE_H + 1}" width="0" height="{LINE_H + 2}">'
            f'<animate attributeName="width" from="0" to="{COLS * CHAR_W}" dur="{dur}s" '
            f'begin="{begin:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        groups.append(
            f'<g clip-path="url(#r{r})"><text x="{PAD}" y="{y}" class="a" xml:space="preserve">{text}</text></g>'
        )
        # Cursor block: appears with the row, rides the wipe edge, then vanishes.
        groups.append(
            f'<rect x="{PAD}" y="{y - LINE_H + 1}" width="{CHAR_W * 1.2:.1f}" height="{LINE_H}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.85;0.85;0" keyTimes="0;0.05;0.95;1" '
            f'begin="{begin:.2f}s" dur="{dur + 0.12}s" fill="freeze"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + COLS * CHAR_W:.1f}" '
            f'begin="{begin:.2f}s" dur="{dur}s" fill="freeze"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait of Andrei-Cristian Popescu">
<rect width="100%" height="100%" fill="{BG}" rx="6"/>
<style>
  .a {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: {FONT_SIZE}px; fill: {FG}; }}
</style>
<defs>{"".join(clips)}</defs>
{"".join(groups)}
</svg>
'''
    Path("avi-ascii.svg").write_text(svg, encoding="utf-8")
    print(f"wrote avi-ascii.svg ({COLS}x{rows} cells, {width:.0f}x{height:.0f}px)")


if __name__ == "__main__":
    main()
