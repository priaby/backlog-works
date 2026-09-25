---
title: "backlog.works Product Backlog"
doc_type: planning
status: active
owners: ["Product Owner"]
tags: ["backlog", "product"]
updated: 2026-09-25
related: ["docs/ops/handoff-2026-09-25.md"]
---

# backlog.works Product Backlog

Document order is priority order. The Product Owner orders this table;
the team works the highest-priority `Planned` or `In Progress` row and
pulls the next only after the current one is merged, deployed, and
reported for Product Owner review, or is parked as `Waiting` with its
external condition named. All rows below are seeded from the Crest
extraction inventory and start `Proposed` — the Product Owner orders and
promotes them.

> [!info] Status legend
> `Proposed` — candidate, not yet ordered or approved by the Product Owner.
> `Ready` — approved, not yet scheduled.
> `Planned` — scheduled for the current Sprint.
> `In Progress` — actively being worked.
> `Waiting` — blocked on an external condition (named in the row).
> `Ready for Product Owner review` — implemented, awaiting acceptance.
> `Done` — accepted by the Product Owner.
> `Cancelled` — will not be done.

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| PBI-001. Extract backlog source module | Read and write the backlog file without Crest's account system | Port `backlog_source.py`'s GitHub Contents API read (ETag cache) and validated reorder/commit path; replace Crest-specific owner/repo/path/committer constants with config. See Crest's `artifacts/checks/backlog-works-extraction-inventory-2026-09-25.md` Section A/E. | Proposed | Team |
| PBI-002. Extract renderer/board | See the backlog as readable cards on a phone | Port `admin_content.py`'s markdown-to-HTML injection technique and `backlog-board.html`'s card renderer; swap Crest brand CSS/JS for a new, unbranded design. | Proposed | Team |
| PBI-003. Standalone sign-in (magic-link email) | Sign in as the Product Owner without Crest's account system | Replace Crest's owner-session + step-up flow (Section D of the inventory) with a magic-link email sign-in scoped to this product only. | Proposed | Team |
| PBI-004. API key for agents | Let an agentic team read and write the backlog without a human session | Issue a per-repo API key with the same write-path validation as the web reorder path (same id set, same per-row cell count, only order changes). | Proposed | Team |
| PBI-005. Railway deploy of a hello-world service on backlog.works | Prove the deploy path works before building product on top of it | Stand up the smallest possible service on Railway, wire the `backlog.works` domain, confirm it answers over HTTPS. Uses the `RAILWAY_PAT` secret already in Crest's Bitwarden (UUID `4852b697-a726-4c8b-99f4-b4d000db3493`). | Proposed | Team |
| PBI-006. Brand and landing page | Give the product a public face distinct from Crest | Name, mark, and a one-page pitch at `backlog.works` explaining the product (see README "Why"/"How it works"). | Proposed | Team |
| PBI-007. Licence decision | Decide what licence, if any, governs this repo | PO decided 2026-09-25: proprietary, all rights reserved (see LICENSE). | Done | Product Owner |
| PBI-008. Partner pitch one-pager | Have something to show a potential partner or early user | A concise one-pager: problem, how it works, status, ask. Depends on PBI-006 (Brand and landing page) for visual identity. | Proposed | Team |

## Bugs

(none yet)
