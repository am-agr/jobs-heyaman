"""Normalize + filter raw postings down to relevant strategy/consulting/analytics roles."""
import re
from datetime import datetime, timezone

# ---- What counts as the right kind of role -----------------------------------
TITLE_INCLUDE = [
    "consultant", "consulting", "strategy", "strategist", "operations", "analytics",
    "business analyst", "advisory", "associate", "engagement", "transformation",
    "manager", "specialist",
]

# ---- Hard rejects (sector + level noise Aman does not want) -------------------
TITLE_EXCLUDE = [
    "intern", "internship", "fresher", "trainee", "graduate",
    "sales", "telecaller", "bpo", "voice process", "night shift",
    "sap bw", "sap basis", "abap",
    "electrical", "lineman", "substation", "grid", "power distribution",
    "utility", "scada",
    "director", "vice president", " vp ", "partner", "principal",  # too senior
    "pmo coordinator", "project coordinator", "office coordinator",
    "recruiter", "hr executive", "accountant",
]

DESC_EXCLUDE = ["power distribution", "grid operations", "substation"]

# ---- Location whitelist: NCR, Jaipur, Rajasthan-adjoining + remote -----------
LOC_INCLUDE = [
    "gurgaon", "gurugram", "delhi", "noida", "ncr", "ghaziabad", "faridabad",
    "jaipur", "rajasthan", "udaipur", "jodhpur",
    "chandigarh", "mohali", "punjab", "ludhiana",
    "ahmedabad", "gujarat", "indore", "bhopal", "madhya pradesh",
    "lucknow", "uttar pradesh",
    "remote", "work from home", "anywhere in india", "pan india", "hybrid",
]

MIN_LPA = 18  # only enforced when a salary is actually present


def _low(s):
    return (s or "").lower()


def title_ok(title):
    t = _low(title)
    if any(x in t for x in TITLE_EXCLUDE):
        return False
    return any(x in t for x in TITLE_INCLUDE)


def location_ok(loc):
    l = _low(loc)
    if not l:
        return True  # keep unknown-location roles; the UI can still surface them
    return any(x in l for x in LOC_INCLUDE)


def desc_ok(desc):
    d = _low(desc)
    return not any(x in d for x in DESC_EXCLUDE)


def salary_ok(job):
    """Reject only when a numeric salary is present AND clearly below the floor."""
    lpa = job.get("salary_lpa")
    if lpa is None:
        return True
    return lpa >= MIN_LPA


def parse_lpa(salary_min, salary_max):
    """Adzuna gives annual INR figures; convert the max to LPA if plausible."""
    for v in (salary_max, salary_min):
        if v and v > 100000:  # looks like an annual rupee figure
            return round(v / 100000, 1)
    return None


def clean_title(t):
    return re.sub(r"\s+", " ", (t or "").strip())


def keep(job):
    return (
        title_ok(job.get("title"))
        and location_ok(job.get("location"))
        and desc_ok(job.get("description"))
        and salary_ok(job)
    )


def dedupe(jobs):
    seen, out = set(), []
    for j in jobs:
        key = (_low(j.get("title"))[:60], _low(j.get("company"))[:30], _low(j.get("location"))[:20])
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


def normalize(*, title, company, location, description, url, source,
              posted=None, salary=""):
    return {
        "id": _hash(title, company, location),
        "title": clean_title(title),
        "company": clean_title(company),
        "location": clean_title(location) or "India",
        "description": (description or "")[:600],
        "url": url or "#",
        "source": source,
        "posted": posted or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "salary": salary or "",
    }


def _hash(*parts):
    import hashlib
    return hashlib.md5("|".join(_low(p) for p in parts).encode()).hexdigest()[:10]
