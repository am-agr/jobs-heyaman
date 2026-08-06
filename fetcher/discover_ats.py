#!/usr/bin/env python3
"""
discover_ats.py — find which ATS each company uses, and the exact slug.

For every company in companies.DISCOVERY_CANDIDATES it probes each provider's
public endpoint with each candidate slug and reports the ones that actually
return jobs. At the end it prints copy-paste-ready config lines for companies.py.

Run it locally (needs internet):  python fetcher/discover_ats.py
No API keys needed — these are public endpoints.
"""
import sys
import time
import requests

import companies as C

UA = {"User-Agent": "the-job-hunt discovery (+https://heyaman.in)"}
T = 20


def _count(url, kind):
    try:
        r = requests.get(url, headers=UA, timeout=T)
        if r.status_code != 200:
            return None
        j = r.json()
        if kind == "greenhouse":
            return len(j.get("jobs", []))
        if kind == "lever":
            return len(j) if isinstance(j, list) else None
        if kind == "ashby":
            return len(j.get("jobs", []))
        if kind == "smartrecruiters":
            return j.get("totalFound", len(j.get("content", [])))
        if kind == "recruitee":
            return len(j.get("offers", []))
    except Exception:
        return None
    return None


def probe(slug):
    """Return list of (provider, count) that work for this slug."""
    checks = [
        ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"),
        ("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json"),
        ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}"),
        ("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=10"),
        ("recruitee", f"https://{slug}.recruitee.com/api/offers/"),
    ]
    hits = []
    for kind, url in checks:
        n = _count(url, kind)
        if n and n > 0:
            hits.append((kind, n))
        time.sleep(0.15)
    return hits


def main():
    found = {}  # provider -> list of (label, slug)
    print("Probing career-site ATS endpoints (public, no keys)…\n")
    for label, slugs in C.DISCOVERY_CANDIDATES.items():
        best = None
        for slug in slugs:
            hits = probe(slug)
            if hits:
                for provider, n in hits:
                    print(f"  ✓ {label:<20} {provider:<16} slug='{slug}'  ({n} jobs)")
                    found.setdefault(provider, []).append((label, slug))
                best = True
                break
        if not best:
            print(f"  ·  {label:<20} no public feed found for {slugs}")
    print("\n" + "=" * 66)
    if not found:
        print("No public ATS feeds matched. These companies likely use closed\n"
              "enterprise ATS (Workday/SuccessFactors/Taleo). For Workday, grab the\n"
              "tenant/pod/site from dev-tools and add to WORKDAY in companies.py.")
        return
    print("Paste these into fetcher/companies.py:\n")
    names = {"greenhouse": "GREENHOUSE", "lever": "LEVER", "ashby": "ASHBY",
             "smartrecruiters": "SMARTRECRUITERS", "recruitee": "RECRUITEE"}
    for provider, entries in found.items():
        print(f"{names[provider]} = [")
        for label, slug in entries:
            print(f'    ("{label}", "{slug}"),')
        print("]\n")


if __name__ == "__main__":
    sys.exit(main())
