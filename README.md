# The Job Hunt

A private, auto-refreshing radar for strategy / consulting / analytics / operations
roles, ranked against my resume, across a 3-tier company universe. PIN-locked,
encrypted, self-updating twice a day. Zero cost.

## The 3 tiers
- Tier 1 - My list: the firms I named (Kearney, EY-Parthenon, ZS, Deloitte, KPMG...).
- Tier 2 - Relevant + startups: adjacent consulting/analytics + startups (MBB, Tiger
  Analytics, Mu Sigma, Razorpay, CRED, PhonePe...).
- Tier 3 - Might interest me: a broader net (Amazon, Google, Grant Thornton, GCCs...).

Tiers 1 & 2 show by default; flip Tier 3 on from the rail. Tier also nudges the match
score (T1 > T2 > T3). Edit the lists in fetcher/companies.py.

## Flow
GitHub Actions (cron 6:00 / 18:00 IST, or the in-app Refresh button):
1. fetcher/fetch_jobs.py -> Adzuna + company career sites (Greenhouse/Lever/Ashby/
   Workday) -> filters noise, tags each role Tier 1/2/3 -> writes fetcher/jobs.json
   (build artifact, never published).
2. encrypt.js -> inlines jobs, AES-256-GCM encrypts the whole app -> writes
   public/index.html (graffiti unlock page + ciphertext), pushes.
Commit -> Netlify auto-deploy -> jobs.heyaman.in. PIN gate -> in-browser decrypt ->
match % vs. my editable resume.

## One-time setup
1. Adzuna key: sign up at https://developer.adzuna.com/, copy App ID + App Key.
2. Push to GitHub:
   git init && git add . && git commit -m "the job hunt"
   gh repo create jobs-heyaman --private --source=. --push
3. GitHub secrets (Settings -> Secrets and variables -> Actions): ADZUNA_ID, ADZUNA_KEY.
4. Deploy on Netlify - USE IMPORT FROM GIT (not drag-and-drop), so netlify.toml is read
   and the Refresh function is bundled. Publish dir=public, functions=netlify/functions
   are pre-filled.
5. Subdomain: Netlify -> Domain settings -> add jobs.heyaman.in; DNS CNAME jobs ->
   <site>.netlify.app. Wait for HTTPS/SSL - the PIN gate needs https.
6. First run: Actions -> Fetch jobs -> Run workflow. Then it runs itself 6:00 & 18:00 IST.

## Refresh button (fetch on demand)
The in-app Refresh calls a Netlify function that triggers the GitHub fetch workflow.
The GitHub token stays server-side, never in the browser. Set in Netlify -> Site
settings -> Environment variables:
  GH_DISPATCH_TOKEN  fine-grained PAT with "Actions: write" on the repo
  GH_REPO            your-username/jobs-heyaman
  GH_WORKFLOW        optional, default fetch-jobs.yml
  GH_BRANCH          optional, default main
Not set? The button degrades gracefully - reloads the latest deployed data and says so.
New roles from a triggered fetch appear ~2-3 min later (reload to pull the fresh bundle).

## PIN gate
Locked with PIN 2452. The whole app + data are AES-256-GCM encrypted (key via
PBKDF2-SHA256); only ciphertext + the unlock page are public. noindex is set. Change
the PIN with env var SITE_PIN (or SITE_PIN=... node encrypt.js locally) - no code change.
Honest note: a 4-digit PIN is 10,000 combinations and the ciphertext is public, so it's
brute-forceable offline. Great against casual access, not a determined attacker. A short
passphrase in SITE_PIN fixes that instantly.

## Career-site (ATS) feeds
Adzuna is the reliable free backbone. Where a company exposes a public feed, add its slug
in fetcher/companies.py (GREENHOUSE / LEVER / ASHBY / WORKDAY) and those roles come
straight from the source, tagged "Career site". Find a slug: careers page -> dev-tools ->
Network -> look for greenhouse.io, lever.co, ashbyhq.com, or myworkdayjobs.com.

## Tuning
- change tier lists: fetcher/companies.py
- change locations / seniority / exclusions / salary floor: fetcher/filters.py
- edit resume, keywords, match scoring: the My profile panel on the site
- change the PIN: env SITE_PIN
- change refresh times: .github/workflows/fetch-jobs.yml cron (UTC)
- edit the app/design: src/index.template.html, then node encrypt.js
- edit the graffiti gate: the shell() function in encrypt.js

Edit design fast: open src/index.template.html directly (runs unencrypted with sample
data), then node encrypt.js to produce the deployable public/index.html.
