#!/usr/bin/env python3
"""A small typed header: name, role, and a blinking cursor."""
from __future__ import annotations

from pathlib import Path

W = 860
H = 92
BG = "#0d1117"
BORDER = "#21262d"
FG = "#c9d1d9"
DIM = "#6e7681"
ACCENT = "#39d353"
GOLD = "#d4af37"

NAME = "Andrei-Cristian Popescu"
ROLE = "software engineer  ·  security  ·  systems"


def main() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Andrei-Cristian Popescu, software engineer">
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
<text x="26" y="34" class="prompt">andrei@github</text>
<text x="146" y="34" class="prompt dim">~ $</text>
<text x="186" y="34" class="cmd">whoami --long</text>
<rect class="caret" x="330" y="21" width="8" height="17" rx="1" fill="{ACCENT}"/>
<text x="26" y="66" class="name">{NAME}</text>
<circle cx="26" cy="80" r="3" fill="{GOLD}"/>
<text x="38" y="84" class="role">{ROLE}</text>
<style>
  text {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; }}
  .prompt {{ font-size: 12px; fill: {ACCENT}; font-weight: 700; }}
  .prompt.dim {{ fill: {DIM}; font-weight: 400; }}
  .cmd {{ font-size: 12px; fill: {FG}; }}
  .name {{ font-size: 21px; font-weight: 700; fill: #f0f6fc; }}
  .role {{ font-size: 12.5px; fill: {DIM}; }}
  .caret {{ animation: blink 1.05s steps(1) infinite; }}
  @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .caret {{ animation: none; }} }}
</style>
</svg>
'''
    Path("header.svg").write_text(svg, encoding="utf-8")
    print("wrote header.svg")


if __name__ == "__main__":
    main()
