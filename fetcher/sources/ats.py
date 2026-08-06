"""
Direct-from-employer job feeds. Every function pulls a company's own postings
straight from its ATS public JSON — source of truth, always current, no scraping
of fragile HTML. Providers: Greenhouse, Lever, Ashby, SmartRecruiters, Recruitee,
Workday. Config lives in companies.py; use discover_ats.py to find exact slugs.
"""
import re
import requests
from filters import normalize

UA = {"User-Agent": "the-job-hunt radar (+https://heyaman.in)"}
TIMEOUT = 25


def _get(url, **kw):
    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
        if r.status_code == 200:
            return r.json()
        print(f"    HTTP {r.status_code} :: {url}")
    except Exception as e:
        print(f"    error :: {url} :: {e}")
    return None


def _post(url, payload, **kw):
    try:
        r = requests.post(url, headers={**UA, "Content-Type": "application/json"},
                          json=payload, timeout=TIMEOUT, **kw)
        if r.status_code == 200:
            return r.json()
        print(f"    HTTP {r.status_code} :: {url}")
    except Exception as e:
        print(f"    error :: {url} :: {e}")
    return None


def _strip(html):
    return re.sub(r"<[^>]+>", " ", html or "")[:600]


def fetch_greenhouse(boards):
    out = []
    for label, slug in boards:
        data = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
        for j in (data or {}).get("jobs", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=(j.get("location") or {}).get("name", ""),
                description=_strip(j.get("content", "")),
                url=j.get("absolute_url", "#"), source="Career site",
                posted=(j.get("updated_at", "") or "")[:10]))
    print(f"  [greenhouse] {len(out)} postings")
    return out


def fetch_lever(accounts):
    out = []
    for label, slug in accounts:
        data = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        for j in (data or []):
            cat = j.get("categories", {}) or {}
            out.append(normalize(
                title=j.get("text", ""), company=label,
                location=cat.get("location", ""),
                description=(j.get("descriptionPlain", "") or "")[:600],
                url=j.get("hostedUrl", "#"), source="Career site"))
    print(f"  [lever] {len(out)} postings")
    return out


def fetch_ashby(orgs):
    out = []
    for label, slug in orgs:
        data = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
        for j in (data or {}).get("jobs", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=j.get("locationName", "") or j.get("location", ""),
                description=(j.get("descriptionPlain", "") or "")[:600],
                url=j.get("jobUrl", "#"), source="Career site"))
    print(f"  [ashby] {len(out)} postings")
    return out


def fetch_smartrecruiters(companies):
    out = []
    for label, slug in companies:
        data = _get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100")
        for j in (data or {}).get("content", []):
            loc = j.get("location", {}) or {}
            loc_str = ", ".join(x for x in [loc.get("city"), loc.get("country")] if x)
            out.append(normalize(
                title=j.get("name", ""), company=label,
                location=loc_str, description="",
                url=f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
                source="Career site",
                posted=(j.get("releasedDate", "") or "")[:10]))
    print(f"  [smartrecruiters] {len(out)} postings")
    return out


def fetch_recruitee(companies):
    out = []
    for label, slug in companies:
        data = _get(f"https://{slug}.recruitee.com/api/offers/")
        for j in (data or {}).get("offers", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=j.get("location", "") or j.get("city", ""),
                description=_strip(j.get("description", "")),
                url=j.get("careers_url", "#"), source="Career site",
                posted=(j.get("published_at", "") or "")[:10]))
    print(f"  [recruitee] {len(out)} postings")
    return out


def fetch_workday(feeds):
    """Each feed: (label, tenant, pod, site). Find via dev-tools -> Network on the
    careers page: https://<tenant>.<pod>.myworkdayjobs.com/.../<site>"""
    out = []
    for label, tenant, pod, site in feeds:
        host = f"https://{tenant}.{pod}.myworkdayjobs.com"
        url = f"{host}/wday/cxs/{tenant}/{site}/jobs"
        data = _post(url, {"appliedFacets": {}, "limit": 20, "offset": 0,
                           "searchText": "strategy consulting operations analytics"})
        for j in (data or {}).get("jobPostings", []):
            out.append(normalize(
                title=j.get("title", ""), company=label,
                location=j.get("locationsText", ""),
                description=(j.get("bulletFields", [""]) or [""])[0],
                url=host + j.get("externalPath", ""), source="Career site"))
    print(f"  [workday] {len(out)} postings")
    return out
