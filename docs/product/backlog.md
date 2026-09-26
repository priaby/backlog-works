---
title: "backlog.works Product Backlog"
doc_type: planning
status: active
owners: ["Product Owner"]
tags: ["backlog", "product"]
updated: 2026-09-26
related: ["docs/ops/handoff-2026-09-25.md"]
---

# backlog.works Product Backlog

Document order is priority order. The Product Owner orders this table and
selects `Ready` items into a Sprint (`In Progress`); the team works the
highest `In Progress` row first and reports it for acceptance, or parks it
with `Waiting on: <condition>` in its Status cell. Rows below are seeded
from the Crest extraction inventory as ordinary items.

> [!info] Status legend (Product Owner decision 2026-09-26)
> An ordinary item has an empty Status cell. Three statuses exist:
> `Ready` — meets the Definition of Ready after refinement and "can be Done
> by the Scrum Team within one Sprint", so it is "ready for selection in a
> Sprint Planning event" (Scrum Guide 2020, Product Backlog; ScrumPLoP
> pattern "Definition of Ready").
> `In Progress` — selected into the current Sprint, i.e. part of the Sprint
> Backlog (Scrum Guide 2020, Sprint Backlog).
> `Done` — meets the Definition of Done and is accepted by the Product
> Owner (Scrum Guide 2020, Commitment: Definition of Done).
> Item ids are one letter plus three digits (`K417`), assigned at creation,
> never reused (Product Owner decision 2026-09-26).
> Notes go after `<br>`: `Sprint: S4`, `Waiting on: <condition>`. An item
> that did not get Done "returns to the Product Backlog" by dropping its
> status. Cancelled items are deleted; git history keeps them.

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| J709. Extract backlog source module | Read and write the backlog file without Crest's account system | Port `backlog_source.py`'s GitHub Contents API read (ETag cache) and validated reorder/commit path; replace Crest-specific owner/repo/path/committer constants with config. See Crest's `artifacts/checks/backlog-works-extraction-inventory-2026-09-25.md` Section A/E. |  | Team |
| U695. Extract renderer/board | See the backlog as readable cards on a phone | Port `admin_content.py`'s markdown-to-HTML injection technique and `backlog-board.html`'s card renderer; swap Crest brand CSS/JS for a new, unbranded design. |  | Team |
| N835. Standalone sign-in (magic-link email) | Sign in as the Product Owner without Crest's account system | Replace Crest's owner-session + step-up flow (Section D of the inventory) with a magic-link email sign-in scoped to this product only. |  | Team |
| F196. API key for agents | Let an agentic team read and write the backlog without a human session | Issue a per-repo API key with the same write-path validation as the web reorder path (same id set, same per-row cell count, only order changes). |  | Team |
| F122. Railway deploy of a hello-world service on backlog.works | Prove the deploy path works before building product on top of it | Stand up the smallest possible service on Railway, wire the `backlog.works` domain, confirm it answers over HTTPS. Uses the `RAILWAY_PAT` secret already in Crest's Bitwarden (UUID `4852b697-a726-4c8b-99f4-b4d000db3493`). Implemented 2026-09-25: service `backlog-works` on Railway, `https://backlog.works` answers `HTTP/2 200` and `/healthz` returns `ok` (receipt in `docs/ops/handoff-2026-09-25.md`); deploy path is `scripts/deploy.sh`. Accepted by the Product Owner 2026-09-26. | Done | Team |
| G761. Brand and landing page | Give the product a public face distinct from Crest | Name, mark, and a one-page pitch at `backlog.works` explaining the product (see README "Why"/"How it works"). |  | Team |
| V645. Licence decision | Decide what licence, if any, governs this repo | PO decided 2026-09-25: proprietary, all rights reserved (see LICENSE). | Done | Product Owner |
| G513. Partner pitch one-pager | Have something to show a potential partner or early user | A concise one-pager: problem, how it works, status, ask. Depends on G761 (Brand and landing page) for visual identity. |  | Team |

