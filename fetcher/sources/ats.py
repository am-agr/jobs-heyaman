"""Direct-from-company ATS feeds. All free, all public JSON. Precision > recall:
these return only the named company's own openings, so they never bring noise."""
import requests
from filters import normalize

UA = {"User-Agent": "jobs.heyaman.in radar (+https://heyaman.in)"}


def _get(url, **kw):
    try:
        r = requests.get(url, headers=UA, timeout=25, **kw)
        if r.status_code == 200:
            return r.json()
        print(f"    HTTP {r.status_code} :: {url}")
    except requests.RequestException as e:
        print(f"    error :: {url} :: {e}")
    return None


def fetch_greenhouse(boards):
    out = []
    for label, token in boards:
        data = _get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
        for j in (data or {}).get("jobs", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=(j.get("location") or {}).get("name", ""),
                description=_strip(j.get("content", "")),
                url=j.get("absolute_url", "#"), source="Greenhouse",
                posted=(j.get("updated_at", "") or "")[:10],
            ))
    print(f"  [greenhouse] {len(out)} postings")
    return out


def fetch_lever(accounts):
    out = []
    for label, acct in accounts:
        data = _get(f"https://api.lever.co/v0/postings/{acct}?mode=json")
        for j in (data or []):
            cat = j.get("categories", {}) or {}
            out.append(normalize(
                title=j.get("text", ""), company=label,
                location=cat.get("location", ""),
                description=j.get("descriptionPlain", "")[:600],
                url=j.get("hostedUrl", "#"), source="Lever",
            ))
    print(f"  [lever] {len(out)} postings")
    return out


def fetch_ashby(orgs):
    out = []
    for label, slug in orgs:
        data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
        for j in (data or {}).get("jobs", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=j.get("locationName", ""),
                description=j.get("descriptionPlain", "")[:600],
                url=j.get("jobUrl", "#"), source="Ashby",
            ))
    print(f"  [ashby] {len(out)} postings")
    return out


def fetch_workday(feeds):
    """Workday CXS search endpoint. Each feed: (label, tenant, wd_pod, site)."""
    out = []
    for label, tenant, pod, site in feeds:
        url = f"https://{tenant}.{pod}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        try:
            r = requests.post(url, headers={**UA, "Content-Type": "application/json"},
                              json={"appliedFacets": {}, "limit": 20, "offset": 0,
                                    "searchText": "strategy consulting operations"}, timeout=25)
            if r.status_code != 200:
                print(f"    HTTP {r.status_code} :: {url}")
                continue
            host = f"https://{tenant}.{pod}.myworkdayjobs.com"
            for j in r.json().get("jobPostings", []):
                out.append(normalize(
                    title=j.get("title", ""), company=label,
                    location=j.get("locationsText", ""),
                    description=j.get("bulletFields", [""])[0] if j.get("bulletFields") else "",
                    url=host + j.get("externalPath", ""), source="Workday",
                    posted=_wd_date(j.get("postedOn", "")),
                ))
        except requests.RequestException as e:
            print(f"    error :: {url} :: {e}")
    print(f"  [workday] {len(out)} postings")
    return out


def _strip(html):
    import re
    return re.sub(r"<[^>]+>", " ", html or "")[:600]


def _wd_date(s):
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")  # Workday gives "Posted 3 Days Ago"
