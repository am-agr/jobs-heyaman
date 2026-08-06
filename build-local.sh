#!/usr/bin/env bash
# Fetch real jobs with your Adzuna key and build public/index.html locally.
# Usage:  ADZUNA_ID=xxx ADZUNA_KEY=yyy ./build-local.sh
set -e
: "${ADZUNA_ID:?Set ADZUNA_ID (get a free key at https://developer.adzuna.com/)}"
: "${ADZUNA_KEY:?Set ADZUNA_KEY}"
echo "Installing deps…"
pip install -q -r fetcher/requirements.txt
echo "Fetching jobs from Adzuna…"
python fetcher/fetch_jobs.py
echo "Encrypting page (PIN ${SITE_PIN:-2452})…"
node encrypt.js
echo ""
echo "Done. Now drag the 'public' folder onto Netlify (or run: netlify deploy --prod --dir=public)."
echo "The number printed above ('kept after filter+dedupe: N') is how many real roles you got."
