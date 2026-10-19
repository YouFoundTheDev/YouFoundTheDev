#!/usr/bin/env python3
"""Render data/contributions.json as an animated contribution heatmap SVG."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
FG = "#c9d1d9"
DIM = "#8b949e"

CELL = 11
GAP = 3
PITCH = CELL + GAP
LEFT = 34
TOP = 30
RIGHT = 16
BOTTOM = 56

WEEKS = 53
DAYS = 7


def week_start(d: date) -> date:
    # GitHub columns run Sunday -> Saturday.
    return d - timedelta(days=(d.weekday() + 1) % 7)


def main() -> None:
    data = json.loads(Path("data/contributions.json").read_text(encoding="utf-8"))
    days = data["days"]

    parsed = [(date.fromisoformat(d["date"]), d) for d in days]
    origin = week_start(min(d for d, _ in parsed))

    grid = {}
    for d, rec in parsed:
        col = (d - origin).days // 7
        row = (d - origin).days % 7
        if 0 <= col < WEEKS:
            grid[(col, row)] = rec

    width = LEFT + WEEKS * PITCH + RIGHT
    height = TOP + DAYS * PITCH + BOTTOM

    cells = []
    for (col, row), rec in sorted(grid.items(), key=lambda kv: (kv[0][0] + kv[0][1], kv[0])):
        level = max(0, min(5, int(rec.get("level", 0))))
        colour = PALETTE[level]
        x = LEFT + col * PITCH
        y = TOP + row * PITCH
        delay = 0.012 * (col + row * 1.6)
        title = f'{rec["count"]} on {rec["date"]}'
        cells.append(
            f'<rect class="cell" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" rx="2.4" fill="{colour}"><title>{title}</title></rect>'
        )

    # Month labels above the first column of each month.
    months = []
    seen = set()
    last_col = -99
    for d, _ in sorted(parsed):
        key = (d.year, d.month)
        if key in seen:
            continue
        seen.add(key)
        col = (d - origin).days // 7
        if 0 <= col < WEEKS and col - last_col >= 3:
            months.append(
                f'<text x="{LEFT + col * PITCH}" y="{TOP - 9}" class="m">{d.strftime("%b")}</text>'
            )
            last_col = col

    weekday_labels = []
    for row, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        weekday_labels.append(
            f'<text x="{LEFT - 8}" y="{TOP + row * PITCH + CELL - 2}" text-anchor="end" class="m">{name}</text>'
        )

    legend_x = width - RIGHT - 5 * (CELL + 2) - 34
    legend = []
    for i, c in enumerate(PALETTE[:5]):
        legend.append(
            f'<rect x="{legend_x + i * (CELL + 2)}" y="{height - 22}" width="{CELL}" height="{CELL}" rx="2.4" fill="{c}"/>'
        )
    legend.append(f'<text x="{legend_x - 6}" y="{height - 12}" text-anchor="end" class="m">Less</text>')
    legend.append(
        f'<text x="{legend_x + 5 * (CELL + 2) + 4}" y="{height - 12}" class="m">More</text>'
    )

    total = f'{data["total"]:,}'
    best = data.get("best_day") or {}
    best_txt = f'best day {best.get("count", 0)} on {best.get("date", "")}' if best else ""
    footer = (
        f'<text x="{LEFT}" y="{height - 12}" class="stat">'
        f'{total} contributions in the last year'
        f'</text>'
        f'<text x="{LEFT + 250}" y="{height - 12}" class="stat">'
        f'longest streak {data["longest_streak"]}d'
        f'</text>'
        f'<text x="{LEFT + 400}" y="{height - 12}" class="stat">{best_txt}</text>'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap">
<rect width="100%" height="100%" fill="{BG}" rx="7"/>
<style>
  .m {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 9.5px; fill: {DIM}; }}
  .stat {{ font-family: "SFMono-Regular", Consolas, Menlo, monospace; font-size: 10.5px; fill: {FG}; }}
  .cell {{ animation: reveal 0.26s ease-out both; }}
  @keyframes reveal {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .cell {{ animation: none; }} }}
</style>
{"".join(months)}
{"".join(weekday_labels)}
{"".join(cells)}
{"".join(legend)}
{footer}
</svg>
'''
    Path("contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print(f"wrote contrib-heatmap.svg ({len(cells)} cells, {width}x{height}px)")


if __name__ == "__main__":
    main()
