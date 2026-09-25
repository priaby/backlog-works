---
name: backlog-works-report
description: Write a Product Owner report, close a session with a handoff under docs/ops/, or take over from a previous session's handoff. Use at session start and at every milestone.
---

# backlog.works Reports and Handoffs

The Product Owner reads reports on a phone, usually between other things.
One report per milestone; never "still running" or "no change" messages.

## Session start (takeover)

1. Read `AGENTS.md`, then the newest `docs/ops/handoff-*.md` (index in
   `docs/ops/README.md`), then `docs/product/backlog.md`.
2. Run `scripts/check.sh`. Note the state of anything the last handoff left
   open (domain, deploy, decisions) and re-verify it with a live command
   before repeating its claim.
3. Pick the active item per `.agents/skills/backlog-works-backlog/SKILL.md`.
   The first report of the session states what the session can operate
   (GitHub, Bitwarden, Railway CLI, local Python) and any gap.

## Report shape (every report, in this order)

1. **Where we stand** — at most 5 fact bullets, each with evidence (SHA,
   URL + status code, check output, file path only when the PO must open it).
2. **Your action items** — numbered, each with the exact step and why only
   the Product Owner can do it; or "none".
3. **What the team does next** — one or two lines.

Name every PBI and bug in full on every mention. Do not ask the Product
Owner to pick a model, an implementation detail, or a design already
covered by precedent in this repo. Anything genuinely PO-only (account
sign-ins, token creation, vault writes, brand and licence calls, backlog
ordering) goes in the action items and in the handoff, not in a mid-task
question.

## Handoff (session close)

Append a dated section to `docs/ops/handoff-<YYYY-MM-DD>.md` (create it
for a new day; frontmatter `title`, `doc_type: handoff`, `status`, `date`)
and keep `docs/ops/README.md` pointing at the newest file. Contents:

- What changed: commits (short SHA + subject), files, deploys with ids.
- Receipts: exact commands and their observed output, no estimates.
- Product Owner decisions resolved this session, with the date.
- Open Product Owner decisions.
- Team proposals (ideas that are not PBIs until the PO says so).
- Not done / parked, with the blocking condition named.

Never put a secret value, token, or private personal data in a handoff;
names and UUIDs only. Commit the handoff with the work it describes.
