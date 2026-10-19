#!/usr/bin/env python3
"""Turn source-prepped.png into a monochrome, self-typing ASCII SVG.

Rows wipe left to right on a short stagger. The base state is fully visible, so
the portrait still reads if animations are disabled or reduced-motion is on.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright -> dark
COLS = 100
CHAR_W = 4.3
FONT_SIZE = 7.4
LINE_H = 7.9
PAD = 10
FG = "#8b949e"
BG = "#0d1117"


def main() -> None:
    src = Path("source-prepped.png")
    if not src.exists():
        raise SystemExit("run scripts/prep_photo.py first")

    img = Image.open(src).convert("L")
    w, h = img.size
    rows = max(12, int(COLS * (h / w) * 0.5))
    img = img.resize((COLS, rows), Image.LANCZOS)

    px = np.asarray(img).astype(np.float32)
    lo, hi = np.percentile(px, [4, 96])
    if hi > lo:
        px = np.clip((px - lo) / (hi - lo), 0.0, 1.0) * 255.0
    brightness = (px / 255.0) ** 1.05
    idx = np.clip(((1.0 - brightness) * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)

    width = COLS * CHAR_W + PAD * 2
    height = rows * LINE_H + PAD * 2

    lines = []
    for r in range(rows):
        y = PAD + r * LINE_H
        text = "".join(RAMP[i] for i in idx[r])
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        delay = 0.045 * r
        lines.append(
            f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{text}</text></g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait of Andrei-Cristian Popescu">
<rect width="100%" height="100%" fill="{BG}" rx="6"/>
<style>
  text {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
          font-size: {FONT_SIZE}px; fill: {FG}; white-space: pre; }}
  .row {{ animation: wipe 0.30s linear both; }}
  @keyframes wipe {{
    from {{ clip-path: inset(0 100% 0 0); }}
    to   {{ clip-path: inset(0 0 0 0); }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; }} }}
</style>
{"".join(lines)}
</svg>
'''
    Path("avi-ascii.svg").write_text(svg, encoding="utf-8")
    print(f"wrote avi-ascii.svg ({COLS}x{rows} cells, {width:.0f}x{height:.0f}px)")


if __name__ == "__main__":
    main()
