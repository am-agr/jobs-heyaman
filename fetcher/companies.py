"""
Company universe (3 tiers) + how to reach company career sites.

Tier 1  — the firms you named.
Tier 2  — other relevant consulting/analytics firms and startups.
Tier 3  — a broader net of companies that might interest you.

Two source kinds feed the pipeline:
  1. Adzuna         -> broad aggregator across India (company name = search term)
  2. Career sites   -> straight from a company's own ATS (Greenhouse / Lever /
                       Ashby / Workday). Highest precision, fully free.

Most large consulting firms run closed enterprise ATS with no clean public JSON,
so Adzuna's company search is how most of their roles surface. Where a company
DOES expose a public feed, add its slug below and those roles come straight from
the source, tagged "Career site".
"""

# ---- Tier 1: your list ------------------------------------------------------
TIER1 = [
    "Accenture", "Kearney", "EY-Parthenon", "EY", "EXL", "PwC", "Deloitte",
    "KPMG", "Capgemini", "IBM", "ZS Associates", "Zinnov", "Siemens",
    "Schneider Electric", "Mastercard", "Cisco", "Fractal Analytics", "Revolut",
]

# ---- Tier 2: other relevant firms + startups --------------------------------
TIER2 = [
    "McKinsey", "BCG", "Bain", "Strategy&", "Oliver Wyman", "Roland Berger",
    "L.E.K.", "Arthur D. Little", "Alvarez & Marsal", "Thoughtworks",
    "Publicis Sapient", "GEP", "WNS", "Genpact", "Tiger Analytics", "Mu Sigma",
    "LatentView", "Tredence", "Course5", "Gramener", "Sigmoid", "Razorpay",
    "CRED", "PhonePe", "Zomato", "Swiggy", "Groww", "Zerodha", "Meesho",
    "Udaan", "Navi", "upGrad",
]

# ---- Tier 3: broader net ----------------------------------------------------
TIER3 = [
    "Amazon", "Flipkart", "Google", "Microsoft", "Uber", "Walmart", "Paytm",
    "TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra", "Cognizant", "Nagarro",
    "Grant Thornton", "Protiviti", "Nielsen", "Kantar", "American Express",
    "Airtel", "Reliance", "Bosch", "Honeywell", "Philips",
]


import re


def _words(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def _key(entry):
    w = _words(entry)
    if not w:
        return ""
    if len(w) == 1:
        return w[0]
    if all(len(x) <= 2 for x in w):   # acronym written spaced, e.g. "L E K" -> "lek"
        return "".join(w)
    return w[0]                        # multiword name -> first significant word


def _matches(company, entry):
    key = _key(entry)
    if not key:
        return False
    cw = _words(company)
    if len(key) <= 3:                 # short/acronym -> must be a whole word ("ey" != "mckinsey")
        return key in cw
    return any(w == key or w.startswith(key) for w in cw)


def tier_of(company):
    if any(_matches(company, e) for e in TIER1):
        return 1
    if any(_matches(company, e) for e in TIER2):
        return 2
    return 3                          # everything else that passed the filters -> broader net

# ---------------------------------------------------------------------------
# CAREER-SITE (ATS) FEEDS  — the reliable, source-of-truth layer.
# Each list holds (Company label, slug). Fill these using discover_ats.py, which
# probes every provider and prints the exact working (provider, slug) pairs.
# Slug-only providers:
GREENHOUSE = [
    # ("Company", "greenhouse_token"),
]
LEVER = [
    # ("Company", "lever_account"),
]
ASHBY = [
    # ("Company", "ashby_slug"),
]
SMARTRECRUITERS = [
    # ("Company", "smartrecruiters_company_id"),
]
RECRUITEE = [
    # ("Company", "recruitee_subdomain"),
]
# Workday needs 4 fields: (label, tenant, pod, site) — from the careers-page URL
# https://<tenant>.<pod>.myworkdayjobs.com/<locale>/<site>/...
WORKDAY = [
    # ("EXL", "exlservice", "wd1", "EXL_Careers"),
    # ("Mastercard", "mastercard", "wd1", "CorporateCareers"),
]

# Candidate slugs discover_ats.py will probe for each company (brand variants).
# Add/adjust freely; the probe tells you which actually work.
DISCOVERY_CANDIDATES = {
    "ZS Associates": ["zs", "zsassociates"],
    "Fractal Analytics": ["fractal", "fractalanalytics"],
    "Tiger Analytics": ["tigeranalytics", "tiger-analytics"],
    "Mu Sigma": ["musigma", "mu-sigma"],
    "LatentView": ["latentview", "latentviewanalytics"],
    "Tredence": ["tredence"],
    "Sigmoid": ["sigmoid", "sigmoidanalytics"],
    "Course5": ["course5", "course5i"],
    "Gramener": ["gramener"],
    "Razorpay": ["razorpay"],
    "CRED": ["cred", "credclub", "dreamplug"],
    "PhonePe": ["phonepe"],
    "Zomato": ["zomato", "eternal"],
    "Swiggy": ["swiggy", "bundl"],
    "Groww": ["groww", "growwww", "nextbillion"],
    "Zerodha": ["zerodha"],
    "Meesho": ["meesho"],
    "Udaan": ["udaan"],
    "Navi": ["navi", "navitechnologies"],
    "upGrad": ["upgrad"],
    "Publicis Sapient": ["publicissapient", "sapient"],
    "Thoughtworks": ["thoughtworks"],
    "GEP": ["gep", "gepworldwide"],
    "Nagarro": ["nagarro"],
    "Revolut": ["revolut"],
    "Mastercard": ["mastercard"],
    "Cisco": ["cisco"],
}

# ---- Adzuna role phrases (precision handled later by filters) ----------------
ROLE_QUERIES = [
    "strategy consultant",
    "management consultant",
    "operations consultant",
    "business analyst strategy",
    "analytics consultant",
    "operations strategy",
    "consulting associate",
    "strategy analyst",
]
