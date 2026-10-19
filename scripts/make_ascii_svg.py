#!/usr/bin/env python3
"""Turn the prepared avatar into a monochrome ASCII portrait.

Bright pixels map to sparse glyphs, dark pixels to dense ones. The gold glasses
from the avatar are kept as a second, coloured layer so the portrait has one
point of colour instead of turning into flat static.

Rows wipe in left to right. The base state is fully visible, so the portrait
still reads when animations are disabled or reduced motion is requested.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .'-:;=+*csx#%@"   # bright -> dark
COLS = 108
CHAR_W = 4.0
FONT_SIZE = 7.0
LINE_H = 7.6
PAD = 12
FG = "#8b949e"
GOLD = "#d4af37"
BG = "#0d1117"
GOLD_RATIO = 0.30
GLYPH = "#"


def gold_mask(color: Image.Image, size: tuple[int, int]) -> np.ndarray:
    """Return a boolean grid marking cells that are predominantly gold."""
    small = color.resize(size, Image.LANCZOS)
    r, g, b = (np.asarray(small)[:, :, i].astype(np.int16) for i in range(3))
    gold = (r > 85) & (r > b + 45) & (g > b + 25) & (r > g + 5)

    rows, cols = size[1], size[0]
    out = np.zeros((rows, cols), dtype=bool)
    for y in range(rows):
        for x in range(cols):
            if gold[y, x]:
                out[y, x] = True
    return out


def main() -> None:
    gray_path = Path("source-prepped.png")
    if not gray_path.exists():
        raise SystemExit("run scripts/prep_photo.py first")

    img = Image.open(gray_path).convert("L")
    w, h = img.size
    rows = max(12, int(COLS * (h / w) * 0.5))
    img = img.resize((COLS, rows), Image.LANCZOS)

    px = np.asarray(img).astype(np.float32)

    # Stretch only the tones inside the subject. The background is pure white,
    # so including it would flatten the statue into one dense block.
    subject = px < 244
    if subject.any():
        lo, hi = np.percentile(px[subject], [2, 98])
        if hi > lo:
            px = np.clip((px - lo) / (hi - lo), 0.0, 1.0) * 255.0
        px = np.where(subject, px, 255.0)

    brightness = (px / 255.0) ** 1.0
    idx = np.clip(((1.0 - brightness) * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    idx = np.where(subject, idx, 0)

    color_path = Path("source-prepped-color.png")
    gold = np.zeros((rows, COLS), dtype=bool)
    if color_path.exists():
        colour = Image.open(color_path).convert("RGB")
        gold = gold_mask(colour, (COLS, rows))

    width = COLS * CHAR_W + PAD * 2
    height = rows * LINE_H + PAD * 2

    lines = []
    for r in range(rows):
        y = PAD + r * LINE_H
        chars = [RAMP[i] for i in idx[r]]
        delay = 0.030 * r

        plain = "".join(" " if gold[r][c] else chars[c] for c in range(COLS))
        line = f'<g class="row" style="animation-delay:{delay:.2f}s">'
        line += f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{esc(plain)}</text>'

        if gold[r].any():
            spans = gold_line(chars, gold[r])
            line += (
                f'<text class="gold" x="{PAD}" y="{y:.1f}" '
                f'xml:space="preserve">{spans}</text>'
            )
        line += "</g>"
        lines.append(line)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait of Andrei-Cristian Popescu">
<rect width="100%" height="100%" fill="{BG}" rx="6"/>
<style>
  text {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
          font-size: {FONT_SIZE}px; fill: {FG}; white-space: pre; }}
  .row {{ animation: wipe 0.28s linear both; }}
  .gold {{ fill: {GOLD}; animation: glint 1.5s ease-in-out 1.9s 2; }}
  @keyframes glint {{
    0%, 100% {{ opacity: 1; }}
    45%      {{ opacity: 0.55; }}
  }}
  @keyframes wipe {{
    from {{ clip-path: inset(0 100% 0 0); }}
    to   {{ clip-path: inset(0 0 0 0); }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .row, .gold {{ animation: none; }}
  }}
</style>
{"".join(lines)}
</svg>
'''
    Path("avi-ascii.svg").write_text(svg, encoding="utf-8")
    print(f"wrote avi-ascii.svg ({COLS}x{rows} cells, {int(gold.sum())} gold cells)")


def gold_line(chars: list[str], mask: np.ndarray) -> str:
    """Draw the glasses as solid gold glyphs so they read at small sizes.

    The gold is bright, so the normal ramp would pick a space there and the
    layer would disappear. A fixed dense glyph keeps the shape visible.
    """
    return "".join(GLYPH if mask[c] else " " for c in range(len(chars)))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
