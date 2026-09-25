---
name: backlog-works-deploy
description: Deploy backlog.works to Railway, verify the running release, or check domain and deployment status. Docs-only and process-only work does not deploy.
---

# backlog.works Deploy

Hosting facts (project, service, environment ids, domains, token name) live in
`AGENTS.md` under "Infrastructure Facts"; do not restate or guess them.

## The only deploy path

```sh
scripts/deploy.sh
```

Run it from this checkout only. The script resolves its own repo root,
refuses to run if `railway.json` or `app/main.py` is missing (guard added
after the 2026-09-25 incident in which Crest's Dockerfile was uploaded from
the wrong directory), fetches `RAILWAY_PAT` inline from Bitwarden, runs
`railway up` with explicit `--project/--service/--environment` flags, and
polls `https://backlog.works` until `200` or 6 minutes.

Never run `railway up` by hand, never `railway link`, never `set -x` around
the token, never paste the token into a command line or a file.

## Preconditions

- `scripts/check.sh` passes on the commit being deployed.
- The commit is on `main` and pushed; deploy the pushed SHA, not a dirty
  tree. The script prints the short SHA it is deploying.
- No other session reports a deploy in flight (check the latest
  `docs/ops/handoff-*.md`).

## Read-only status commands

Use the `AGENTS.md` command pattern (token via BWS inline, all three scope
flags). Useful subcommands with the project-scoped token:

- `railway status --json` — service and latest deployment state.
- `railway domain status backlog.works` — custom-domain CNAME/cert state.
- `railway logs --deployment <id>` — build/runtime logs.

Account-scope commands (`railway link`, `railway whoami`, project rename)
return `Unauthorized` with this token; that is expected, not a blocker.

## Prove it

A deploy is done only with all three receipts in the report:

1. `railway up` returned a deployment id and the poll saw `200`.
2. `curl -sI https://backlog.works` shows `HTTP/2 200` and
   `curl -s https://backlog.works/healthz` returns `ok`.
3. The generated domain `https://backlog-works-production.up.railway.app`
   also answers `200` on `/healthz` (proves the service, not just DNS).

Record the deployment id, SHA, and timestamps in the day's handoff under
`docs/ops/`. If the poll times out, fetch `railway logs` for the deployment,
classify build failure vs. runtime failure vs. domain/DNS, and report without
retrying blindly.
