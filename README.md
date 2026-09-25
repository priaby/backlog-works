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

## Status

Pre-alpha. Extracted from Crest's admin backlog board (see Origin below) as
a standalone starting point — nothing here is deployed yet.

## Origin

backlog.works started as a feature inside the Crest invoicing product's
admin board (that repository is not public). This repository is a fresh
extraction: a generalized backlog file format, board renderer, and write
path, decoupled from Crest's own accounts, auth, and branding.

## License

To be decided (Product Owner decision pending). No license is granted yet.
