---
name: backlog-works-secrets
description: Fetch or reference the RAILWAY_PAT deploy token, add a runtime secret to Railway, or document a credential for backlog.works. Documentation-only work needs no vault access.
---

# backlog.works Secrets

There is no secrets helper in this repo yet. Until there is, backlog.works
borrows Crest's Bitwarden Secrets Manager helper at
`/home/priaby/Projects/crest/scripts/crest_bws.py` (org `Alpari`, project
`Crest`; local access token in the freedesktop Secret Service entry
`crest.bws.access-token`). Read Crest's
`.agents/skills/bitwarden-secrets/SKILL.md` for the helper's own rules.

## What exists

- `RAILWAY_PAT`, UUID `4852b697-a726-4c8b-99f4-b4d000db3493`: a Railway
  **project token** for project `marvelous-wisdom`. Export it as
  `RAILWAY_TOKEN` (not `RAILWAY_API_TOKEN`). It can deploy and read
  project state; account-scope calls return `Unauthorized`.
- Nothing else. Product secrets (GitHub token for the Contents API, sign-in
  email provider, API-key signing secret) do not exist yet and each is a
  Product Owner vault write when its PBI comes up.

## Rules

- Fetch only inline, as `AGENTS.md`'s command pattern shows; never `get`
  with stdout to the terminal, never `echo`, never `set -x`, never write a
  value to a file, log, handoff, chat message, or shell history.
- Runtime secrets for the deployed service go in Railway project variables
  (`railway variables --set NAME=... ` with the standard scope flags, value
  taken from BWS inline), never in `railway.json`, the Dockerfile, or the
  repo.
- Adding a secret to Bitwarden is done by the Product Owner in the web app;
  list it as an action item with the exact name and consumer, then verify
  the name appears in `crest_bws.py status --show-names` before wiring.
- Documents may carry names and UUIDs only. `scripts/check.sh` greps for
  secret-looking literals; keep it passing.
- A missing grant is a concrete blocker: report the exact non-secret lookup
  that failed and finish the independent work.
