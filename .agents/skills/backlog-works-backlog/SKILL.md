---
name: backlog-works-backlog
description: Read, edit, reorder, or change the status of items in docs/product/backlog.md, or pick the next item to work. Enforces the file format that the product's own write path will parse.
---

# backlog.works Backlog File

`docs/product/backlog.md` is both this repo's Scrum backlog and the first
fixture of the product itself: whatever this file looks like is what the
board renderer and write path (PBI-001 Extract backlog source module,
PBI-002 Extract renderer/board) must parse. Keep it machine-clean.

Run `python3 scripts/check_backlog.py` after every edit; `scripts/check.sh`
runs it too.

## Format contract (inherited from Crest `backlog_source.py`)

- Active table = the **first contiguous run** of lines starting with the
  four characters `| PBI-`. Nothing else locates it, so never put a
  `| PBI-` row anywhere above or in a second block.
- Row shape: `| PBI-<digits>[a-z]. <Title> | <Core Job> | <Context> | <Status> | <Driver> |`
  (id, optional one-letter sub-slice, a literal period, then the title).
  Exactly 5 cells per row, same as the header.
- Status = the text in cell 4 before the first `<br>`; anything after
  `<br>` is free text (sprint tag, note) that must survive reorders
  byte-for-byte.
- Status vocabulary (PO decision 2026-09-26, Scrum Guide grounded): empty
  cell = ordinary item; `Ready` (Definition of Ready met, selectable);
  `In Progress` (in the Sprint Backlog); `Done` (Definition of Done met,
  accepted). Notes after `<br>`: `Sprint: S4`, `Waiting on: <condition>`.
  Cancelled rows are deleted (git history keeps them). Do not invent
  values; configurable statuses are a later product decision.
- Reorder invariants a write path must enforce and an agent must respect
  by hand: same id set, same per-row cell count, row content unchanged
  when only ordering; first-row move is refused unless some row is
  `In Progress`.
- `## Bugs` sits below the table. Bug ids are `BUG-YYYY-MM-DD-slug`; keep
  each entry short (surface, steps, expected, actual, evidence, status).
- Bump `updated:` in the frontmatter on every edit.

## Who may change what

- **Order**, marking `Ready` after refinement, and selecting into the
  Sprint (`Ready` -> `In Progress`) are the Product Owner's. The team never adds a PBI row or reorders on its own
  initiative; new ideas go into the report as proposals.
- **The team** keeps the item `In Progress`, adds `Waiting on:
  <condition>` when parked, and reports it for acceptance with receipts.
  Only the Product Owner sets `Done`, drops a status (item "returns to the
  Product Backlog"), or deletes a row.
- Pick the highest `In Progress` row; if none, report that and stop. Never
  start a `Ready` or ordinary row.

## Naming rule

Every mention of an item, anywhere in a report or doc, is number plus title:
"PBI-002 (Extract renderer/board)". Look the title up in the file; scan the
message for bare `PBI-`/`BUG-` tokens before sending.
