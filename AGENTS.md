# backlog.works Agents Guide

This file is the top-level contract for agents working in this repo. It is
adapted from Crest's `AGENTS.md` (the product this repo was extracted from)
but keeps only what applies to a fresh, pre-alpha repository. Extend it as
the product grows — don't restore Crest-specific sections (deploy hosts,
brand assets, provider logos) unless this product actually needs them.

## File Ownership Map

- `README.md` — positioning, status, origin, license status.
- `AGENTS.md` — this file: workflow contract for agents.
- `docs/product/backlog.md` — the product backlog in the product's own
  format (see below). Product Owner priority order = document order.
- `docs/ops/` — handoffs, infra notes, operational receipts.

## Product Owner Standing Directives

These generalise from Crest's Product Owner directives and apply from an
agent's first message in this repo, without being reminded:

- **Name every PBI and bug in full.** Never a bare index; write the number
  with its title, e.g. "PBI-002 (Extract renderer/board)" — look it up in
  `docs/product/backlog.md`, don't guess. A table may use the number alone
  only when the title appears in the same row.
- **One report per milestone, not per step.** No "waiting"/"still
  running"/"no change" messages. Every report: (1) where things stand —
  fact bullets with evidence; (2) the Product Owner's action items, or
  "none"; (3) what the team does next.
- **Never make the Product Owner a blocker.** Make ordinary design and
  implementation decisions using precedent already in this repo and record
  them; put genuinely PO-only steps (account sign-ins, token creation,
  vault writes, brand/license calls) in the next handoff instead of asking
  mid-task.
- **One PBI in progress at a time.** Work one backlog item at a time; pull
  the next only after the current one is merged and reported for Product
  Owner review, or is parked with its blocking condition named.
- **The team never creates Product Backlog Items on its own.** Work the
  Product Owner asks for happens inside the active item; findings and ideas
  are proposals in the report, and become PBIs only when the Product Owner
  says so.
- **Backlog document order is priority order.** `docs/product/backlog.md`'s
  document order is priority order; work the highest-priority item with
  status `Planned` or `In Progress`.
- **Model routing is the orchestrator's call, not the Product Owner's.**
  Route packets to models by difficulty and quota; never ask the Product
  Owner to pick a model.
- **No readiness claims without a receipt.** Don't say a step waits only on
  a Product Owner decision, or that a capability works, until the real path
  has been exercised end to end with current evidence.

## Infrastructure Facts

- **Hosting:** Railway. Production target is `backlog.works`.
- **Secrets:** live in Railway project variables, not repo files.
- **Bitwarden:** the only secret currently in Crest's Bitwarden Secrets
  Manager relevant to this repo is the Railway deploy token, stored as
  `RAILWAY_PAT` (UUID `4852b697-a726-4c8b-99f4-b4d000db3493`) — name/UUID
  only, never the value, per Crest's Bitwarden secret-handling rule.

## The Backlog File

`docs/product/backlog.md` is the product backlog in the product's own
format: a markdown table whose rows begin `| PBI-<digits>` in the table's
active section, columns `Item (PBI)`, `Core Job`, `Context`, `Status`,
`Driver`, plus a `## Bugs` section below it. See the file itself for the
current status legend. This format (and the row-reorder invariants a future
write path should enforce — same id set, same per-row cell count, only row
order changes) is inherited from Crest's `backlog_source.py` design; keep
compatible with it unless the Product Owner approves a format change.

## Editing Rules

- Keep docs concise, ASCII where practical. No secrets, tokens, passwords,
  or private personal data in repo docs — names and UUIDs only.
- No license header or repo-root LICENSE file until the Product Owner
  decides (see README "License").
