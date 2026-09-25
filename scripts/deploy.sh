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

if [[ ! -f app/main.py ]]; then
  echo "Error: app/main.py not found in $REPO_ROOT — aborting deploy" >&2
  exit 1
fi

# Fetch token inline; never echo it
set +x
RAILWAY_TOKEN="$(python3 /home/priaby/Projects/crest/scripts/crest_bws.py get RAILWAY_PAT | tr -d '[:space:]')"
export RAILWAY_TOKEN
set -x

# Deploy
railway up --service backlog-works --detach

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
    echo "Health check: $healthz"
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
