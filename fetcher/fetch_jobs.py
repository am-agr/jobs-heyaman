#!/usr/bin/env python3
"""
jobs.heyaman.in — fetch pipeline.

Pulls strategy / consulting / analytics openings from Adzuna + direct ATS feeds,
filters out sector & seniority noise, tags target companies, dedupes, and writes
public/data/jobs.json which the site reads. Runs twice daily via GitHub Actions.
"""
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import companies as C
import filters as F
from sources import fetch_adzuna, fetch_greenhouse, fetch_lever, fetch_ashby, fetch_workday

# Build-only artifact — encrypt.js inlines this into the encrypted page,
# so it is never published as a plaintext feed.
OUT = os.path.join(os.path.dirname(__file__), "jobs.json")


def tier(company):
    return C.tier_of(company)


def run():
    print("== jobs.heyaman.in fetch ==")
    raw = []

    # 1. broad net
    raw += fetch_adzuna(C.ROLE_QUERIES)

    # 2. precision ATS feeds
    raw += fetch_greenhouse(C.GREENHOUSE)
    raw += fetch_lever(C.LEVER)
    raw += fetch_ashby(C.ASHBY)
    raw += fetch_workday(C.WORKDAY)

    print(f"total raw: {len(raw)}")

    # 3. filter + dedupe
    kept = [j for j in raw if F.keep(j)]
    kept = F.dedupe(kept)
    for j in kept:
        j["tier"] = tier(j["company"])            # 1 / 2 / 3 / 0
        j.pop("salary_lpa", None)                 # internal-only

    # newest first, then tier (tier 1 floats to top)
    kept.sort(key=lambda j: j.get("posted", ""), reverse=True)
    kept.sort(key=lambda j: (j["tier"] == 0, j["tier"] or 9))

    by_tier = {1: 0, 2: 0, 3: 0, 0: 0}
    for j in kept:
        by_tier[j["tier"]] += 1
    print(f"by tier -> T1:{by_tier[1]}  T2:{by_tier[2]}  T3:{by_tier[3]}  other:{by_tier[0]}")

    print(f"kept after filter+dedupe: {len(kept)}")

    stamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b, %H:%M IST")
    payload = {
        "updated": stamp,
        "count": len(kept),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "jobs": kept,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"wrote {OUT}  ({len(kept)} jobs, updated {stamp})")


if __name__ == "__main__":
    run()
