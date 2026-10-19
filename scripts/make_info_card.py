#!/usr/bin/env python3
"""Neofetch-style info card SVG with a staggered print-in effect.

Every row is visible in the base state and only animated when motion is
allowed, so the card never renders blank.
"""
from __future__ import annotations

import os

W = 500
PAD = 20
ROW_H = 27
HEAD_H = 36
BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#6e7681"
KEY = "#58a6ff"
ACCENT = "#39d353"
GOLD = "#d4af37"

ROWS = [
    ("who", "andrei", "andrei@github"),
    ("sep", "", ""),
    ("kv", "Now", "building Closure and a security platform"),
    ("kv", "Prev", "cybersecurity intern @ DNSC, Bucharest"),
    ("kv", "Stack", "TypeScript  Python  Rust  C/C++  Next.js"),
    ("kv", "Data", "PostgreSQL  SQL  Redis  Docker"),
    ("kv", "Certs", "CompTIA Security+  ·  Microsoft SC-500"),
    ("kv", "Commits", "3,000+  ·  1,700+ tests on the release path"),
    ("sep", "", ""),
    ("palette", "", ""),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    height = HEAD_H + PAD + len(ROWS) * ROW_H + PAD - 6

    parts = []
    y = HEAD_H + PAD
    for i, (kind, label, value) in enumerate(ROWS):
        delay = 0.12 + i * 0.085
        cls = "" if static else f' class="row" style="animation-delay:{delay:.2f}s"'

        if kind == "sep":
            parts.append(
                f'<g{cls}><line x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}" '
                f'stroke="{BORDER}" stroke-dasharray="2 4"/></g>'
            )
        elif kind == "palette":
            swatches = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
            dots = "".join(
                f'<rect x="{PAD + n * 19}" y="{y - 10}" width="11" height="11" rx="2" fill="{c}"/>'
                for n, c in enumerate(swatches)
            )
            dots += (
                f'<rect x="{PAD + 5 * 19}" y="{y - 10}" width="11" height="11" rx="2" fill="{GOLD}"/>'
            )
            parts.append(f'<g{cls}>{dots}</g>')
        elif kind == "who":
            parts.append(
                f'<g{cls}>'
                f'<circle cx="{PAD + 4}" cy="{y - 4}" r="4" fill="{ACCENT}"/>'
                f'<text x="{PAD + 16}" y="{y}" class="user">{esc(label)}</text>'
                f'<text x="{PAD + 92}" y="{y}" class="host">{esc(value)}</text>'
                f'</g>'
            )
        else:
            parts.append(
                f'<g{cls}>'
                f'<text x="{PAD}" y="{y}" class="k">{esc(label)}</text>'
                f'<text x="{PAD + 92}" y="{y}" class="v">{esc(value)}</text>'
                f'</g>'
            )
        y += ROW_H

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Terminal info card for Andrei-Cristian Popescu">
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 8 a8 8 0 0 1 8 -8 h{W - 17} a8 8 0 0 1 8 8 v{HEAD_H - 8} h-{W - 1} z" fill="#161b22"/>
<circle cx="19" cy="18" r="4.5" fill="#ff5f56"/>
<circle cx="34" cy="18" r="4.5" fill="#ffbd2e"/>
<circle cx="49" cy="18" r="4.5" fill="#27c93f"/>
<text x="{W - PAD}" y="22" text-anchor="end" class="title">andrei@github: ~</text>
<line x1="0" y1="{HEAD_H}" x2="{W}" y2="{HEAD_H}" stroke="{BORDER}"/>
<style>
  text {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; }}
  .title {{ font-size: 10.5px; fill: {DIM}; }}
  .user {{ font-size: 13px; font-weight: 700; fill: {ACCENT}; }}
  .host {{ font-size: 13px; fill: {DIM}; }}
  .k {{ font-size: 12.5px; font-weight: 700; fill: {KEY}; }}
  .v {{ font-size: 12.5px; fill: {FG}; }}
  .row {{ animation: print 0.34s ease-out both; }}
  @keyframes print {{
    from {{ opacity: 0.15; }}
    to   {{ opacity: 1; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; }} }}
</style>
{"".join(parts)}
</svg>
'''
    with open("info-card.svg", "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote info-card.svg ({W}x{height}px)")


if __name__ == "__main__":
    main()
