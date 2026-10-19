#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG.

Rows fade and slide in on a short stagger so the panel looks like it is
printing next to the portrait. Set STATIC=1 for a frozen frame.
"""
from __future__ import annotations

import os

W = 500
PAD = 18
ROW_H = 26
HEAD_H = 34

BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
KEY = "#58a6ff"
ACCENT = "#39d353"
WARN = "#d29922"

ROWS = [
    ("key", "andrei", ACCENT, "andrei@github"),
    ("sep", "", "", ""),
    ("kv", "Now", KEY, "building Closure and a security platform"),
    ("kv", "Prev", KEY, "cybersecurity intern @ DNSC, Bucharest"),
    ("kv", "Stack", KEY, "TypeScript  Python  Rust  C/C++  Next.js"),
    ("kv", "Data", KEY, "PostgreSQL  SQL  Redis  Docker"),
    ("kv", "Certs", KEY, "CompTIA Security+  ·  Microsoft SC-500"),
    ("kv", "Commits", KEY, "3,000+  ·  1,700+ tests on the release path"),
    ("sep", "", "", ""),
    ("dots", "", "", ""),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    height = HEAD_H + PAD + len(ROWS) * ROW_H + PAD

    parts = []
    y = HEAD_H + PAD
    for i, (kind, label, colour, value) in enumerate(ROWS):
        delay = 0.18 + i * 0.11
        anim = "" if static else (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.32s" '
            f'begin="{delay:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="10 0" to="0 0" dur="0.32s" begin="{delay:.2f}s" fill="freeze"/>'
        )
        if kind == "sep":
            parts.append(
                f'<g opacity="0"><line x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}" '
                f'stroke="{BORDER}" stroke-dasharray="2 4"/>{anim}</g>'
            )
        elif kind == "dots":
            swatches = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
            dots = "".join(
                f'<rect x="{PAD + n * 20}" y="{y - 11}" width="11" height="11" rx="2" fill="{c}"/>'
                for n, c in enumerate(swatches)
            )
            parts.append(f'<g opacity="0">{dots}{anim}</g>')
        else:
            key = f"{label:>8}" if kind == "kv" else label
            parts.append(
                f'<g opacity="0">'
                f'<text x="{PAD}" y="{y}" class="k" fill="{colour}">{esc(key)}</text>'
                f'<text x="{PAD + 92}" y="{y}" class="v">{esc(value)}</text>'
                f'{anim}</g>'
            )
        y += ROW_H

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Terminal info card for Andrei-Cristian Popescu">
<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="7" fill="{BG}" stroke="{BORDER}"/>
<circle cx="18" cy="17" r="4.5" fill="#ff5f56"/>
<circle cx="33" cy="17" r="4.5" fill="#ffbd2e"/>
<circle cx="48" cy="17" r="4.5" fill="#27c93f"/>
<text x="{W - PAD}" y="21" text-anchor="end" class="title">~/README.md</text>
<line x1="0" y1="{HEAD_H}" x2="{W}" y2="{HEAD_H}" stroke="{BORDER}"/>
<style>
  .title {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 11px; fill: {DIM}; }}
  .k {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 12.5px; font-weight: 700; }}
  .v {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 12.5px; fill: {FG}; }}
</style>
{"".join(parts)}
</svg>
'''
    with open("info-card.svg", "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote info-card.svg ({W}x{height}px)")


if __name__ == "__main__":
    main()
