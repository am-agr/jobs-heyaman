"""Adzuna India source. Free API — get app_id + app_key at
https://developer.adzuna.com/ and set them as env vars ADZUNA_ID / ADZUNA_KEY."""
import os
import time
import requests

from filters import normalize, parse_lpa

BASE = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"


def fetch_adzuna(queries, locations=("delhi", "gurgaon", "jaipur", "noida"), pages=1):
    app_id = os.environ.get("ADZUNA_ID")
    app_key = os.environ.get("ADZUNA_KEY")
    if not app_id or not app_key:
        print("  [adzuna] no ADZUNA_ID / ADZUNA_KEY set — skipping")
        return []

    out = []
    for q in queries:
        for loc in locations:
            for page in range(1, pages + 1):
                params = {
                    "app_id": app_id,
                    "app_key": app_key,
                    "what": q,
                    "where": loc,
                    "results_per_page": 25,
                    "max_days_old": 21,
                    "content-type": "application/json",
                }
                try:
                    r = requests.get(BASE.format(page=page), params=params, timeout=25)
                    if r.status_code != 200:
                        print(f"  [adzuna] {q}/{loc} -> HTTP {r.status_code}")
                        continue
                    for j in r.json().get("results", []):
                        lpa = parse_lpa(j.get("salary_min"), j.get("salary_max"))
                        rec = normalize(
                            title=j.get("title", ""),
                            company=(j.get("company") or {}).get("display_name", "Unknown"),
                            location=(j.get("location") or {}).get("display_name", ""),
                            description=j.get("description", ""),
                            url=j.get("redirect_url", "#"),
                            source="Adzuna",
                            posted=(j.get("created", "") or "")[:10],
                            salary=f"~₹{lpa} LPA" if lpa else "",
                        )
                        rec["salary_lpa"] = lpa
                        out.append(rec)
                except requests.RequestException as e:
                    print(f"  [adzuna] {q}/{loc} error: {e}")
                time.sleep(0.4)  # be polite to the free tier
    print(f"  [adzuna] collected {len(out)} raw postings")
    return out
