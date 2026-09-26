# backlog.works

backlog.works is a Scrum product backlog shared by a human Product Owner and
agentic teams. The backlog is a markdown file in your repo; the web app
gives the Product Owner a phone-sized hand on ordering and acceptance;
agents read and write it with an API key.

## Why

Agentic teams already write and read plenty of markdown in-repo, and a
human Product Owner still needs to see, reorder, and accept work — often
from a phone, in a spare minute, not at a desk running a full dev
environment. Most backlog/PM tools assume the opposite split: a human-first
web UI with agents bolted on as an integration. backlog.works starts from
the file-in-repo as the source of truth and builds the smallest useful
surface for a human to steer it.

## How it works

- **The file in your repo is the source of truth.** Your product backlog
  lives at `docs/product/backlog.md` (or wherever you configure), in plain
  markdown, versioned like any other file.
- **The web view reads and writes via GitHub.** The Product Owner opens a
  phone-sized board, reorders or updates items, and backlog.works commits
  the change back to your repo through the GitHub API — no separate
  database of record.
- **Agents read and write it via git or API.** Your agentic team edits the
  backlog file directly through normal git operations, or through a
  backlog.works API key when it needs the same commit path the web view
  uses.

## Run locally

`PORT=8080 PYTHONPATH=src python3 -m backlogworks` -- serves `/` (placeholder page) and `/healthz` (`200 ok`) on `0.0.0.0:$PORT`, stdlib only, no dependencies.

`scripts/check.sh` -- repo gate: backlog file format, architecture rules, Python compile, unit tests, app smoke test, skill wiring, secret-literal scan.

`/` serves the pitch plus a fictitious product backlog ("Lighthouse") rendered by the one board engine every tenant will use. Architecture: `docs/architecture.md`.

## Working in this repo with agents

`AGENTS.md` is the contract (imported by `CLAUDE.md`). Task-specific
skills live in `.agents/skills/` (mirrored as symlinks in
`.claude/skills/`): deploy, backlog file editing, reports and handoffs,
porting from Crest, secrets handling.

## Status

Pre-alpha. Extracted from Crest's admin backlog board (see Origin below) as
a standalone starting point. A placeholder service is live at
`https://backlog.works`; no product code is ported yet.

## Origin

backlog.works started as a feature inside the Crest invoicing product's
admin board (that repository is not public). This repository is a fresh
extraction: a generalized backlog file format, board renderer, and write
path, decoupled from Crest's own accounts, auth, and branding.

## License

License: proprietary, all rights reserved (see LICENSE). The repository is
public for visibility; this is a commercial product, not open source.
