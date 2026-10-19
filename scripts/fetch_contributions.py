#!/usr/bin/env python3
"""Fetch the public contribution calendar and write data/contributions.json.

No token: GitHub serves the same calendar fragment the profile page uses at
https://github.com/users/<username>/contributions
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "YouFoundTheDev"
URL = f"https://github.com/users/{USERNAME}/contributions"


def parse_count(text: str) -> int:
    if "No contributions" in text:
        return 0
    m = re.search(r"([\d,]+)\s+contribution", text)
    return int(m.group(1).replace(",", "")) if m else 0


def main() -> None:
    resp = requests.get(
        URL,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme)"},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tips = {
        t.get("for"): t.get_text(" ", strip=True)
        for t in soup.select("tool-tip")
        if t.get("for")
    }

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        raw = cell.get("data-date")
        if not raw:
            continue
        count = parse_count(tips.get(cell.get("id"), ""))
        days.append(
            {
                "date": raw,
                "count": count,
                "level": int(cell.get("data-level") or 0),
            }
        )

    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells parsed; GitHub markup may have changed")

    counts = [d["count"] for d in days]
    total = sum(counts)

    # Streaks
    longest = current = 0
    for c in counts:
        current = current + 1 if c > 0 else 0
        longest = max(longest, current)
    current = 0
    for c in reversed(counts):
        if c > 0:
            current += 1
        else:
            break

    monthly = Counter()
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    best = max(days, key=lambda d: d["count"]) if days else None

    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly": dict(sorted(monthly.items())),
        "days": days,
    }

    out = Path("data/contributions.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {out} ({total} contributions, {len(days)} days)")


if __name__ == "__main__":
    main()
