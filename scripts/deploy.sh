#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root from script location
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Safety check: prevent deploying from the wrong checkout
if [[ ! -f railway.json ]]; then
  echo "Error: railway.json not found in $REPO_ROOT — aborting deploy" >&2
  exit 1
fi

if [[ ! -f src/backlogworks/__main__.py ]]; then
  echo "Error: src/backlogworks/__main__.py not found in $REPO_ROOT — aborting deploy" >&2
  exit 1
fi

# Railway scope (AGENTS.md "Infrastructure Facts"): always explicit flags,
# never `railway link` (Unauthorized for the project-scoped token).
RAILWAY_PROJECT="a611baf5-ab5c-432f-9370-88dab8c378c7"
RAILWAY_SERVICE="backlog-works"
RAILWAY_ENVIRONMENT="production"

# Fetch token inline; never echo, trace, or persist it. Do not enable `set -x`
# anywhere in this script.
RAILWAY_TOKEN="$(python3 /home/priaby/Projects/crest/scripts/crest_bws.py get RAILWAY_PAT | tr -d '[:space:]')"
[[ -n "$RAILWAY_TOKEN" ]] || { echo "Error: empty RAILWAY_PAT from Bitwarden" >&2; exit 1; }
export RAILWAY_TOKEN

echo "Deploying $(git rev-parse --short HEAD) from $REPO_ROOT to service $RAILWAY_SERVICE ($RAILWAY_ENVIRONMENT)"
railway up --service "$RAILWAY_SERVICE" --project "$RAILWAY_PROJECT" \
  --environment "$RAILWAY_ENVIRONMENT" --detach

# Poll for deployment completion (6 minutes max, 20s interval)
echo "Polling https://backlog.works for deployment readiness..."
max_attempts=18  # 18 * 20s = 360s = 6 minutes
attempt=0

while (( attempt < max_attempts )); do
  attempt=$((attempt + 1))
  status_line=$(curl -sI --max-time 10 https://backlog.works 2>/dev/null | head -1 || echo "")

  if [[ -n "$status_line" && "$status_line" =~ 200 ]]; then
    echo "Deployment ready. Status: $status_line"
    healthz=$(curl -s --max-time 10 https://backlog.works/healthz 2>/dev/null || echo "")
    generated=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
      https://backlog-works-production.up.railway.app/healthz 2>/dev/null || echo "000")
    echo "Health check: backlog.works/healthz=$healthz generated-domain/healthz=$generated"
    exit 0
  fi

  if (( attempt < max_attempts )); then
    echo "Attempt $attempt/$max_attempts: $status_line (retrying in 20s...)"
    sleep 20
  fi
done

echo "Timeout: deployment did not reach 200 within 6 minutes." >&2
echo "Final status: $status_line" >&2
exit 1
