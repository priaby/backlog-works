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
selects items into the Sprint; the team works the highest `In Progress`
row first. This file is what `https://backlog.works` renders: the
product's first tenant is itself.

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
| U695. Board on the phone: status views, reorder controls, design foundations | Read and reorder the backlog on a phone without opening the markdown | One board engine for every tenant and the landing: segmented view selector, up / down / top controls, a design system so no component is invented twice. Order changes preview locally until J709 (Persist backlog changes to the repo) lands. | In Progress<br>Sprint: S1 | Team |
| J709. Persist backlog changes to the repo | Move a card from a phone and have the file in the repo change in the same commit | `BacklogSource` over the GitHub Contents API: ETag-cached read, validated reorder and status change on raw row slices (same ids, same cell counts, nothing else changes), commit guarded by the blob `sha`, push webhook drops the cache. |  | Team |
| N835. Product Owner sign-in (magic-link email) | Sign in from a phone with no password and no Crest account | Magic link via the Mailjet sub-account (`MAIL_FROM=noreply@backlog.works`), session cookie, CSRF, sign-out. Waiting on the three Mailjet TXT records in Railway DNS before mail can send. |  | Team |
| F196. API key for agents | Let an agentic team read and write the backlog without a human session | Per-repo API key; the same write-path validation as the web reorder path; key ids in the timeline, never key values. |  | Team |
| R685. Configurable statuses per backlog | Use the team's own workflow words without asking the vendor | The legend block in the markdown declares the vocabulary and its order; parser, checker, selector and pills follow it; the default stays the four Scrum-grounded states. |  | Team |
| R905. Live updates on the phone | See a teammate's or an agent's change without reloading | Server-sent events after every commit and every webhook, reconnect-safe, no third-party service (architecture section 3, "Freshness"). |  | Team |
| G761. Brand and landing page | Give the product a public face distinct from Crest | Name, mark, one-paragraph pitch above the board, meta tags and a share image; nothing that competes with the board for attention. |  | Team |
| C949. Product documentation at /docs | Set up a repo in ten minutes without asking anyone | File format and status legend, id scheme, how ordering and acceptance work, API reference; served from markdown packaged in the image. |  | Team |
| K507. Item type field | Tell a bug from a feature on the board | Optional type column or legend-declared types (`bug`, `chore`); type chip on the card; no separate bug section. Product Owner note 2026-09-26: "might be later". |  | Team |
| G513. Partner pitch one-pager | Have something to show a potential partner or early user | Problem, how it works, status, ask. Depends on G761 (Brand and landing page) for visual identity. |  | Team |
| F122. Railway deploy of a hello-world service on backlog.works | Prove the deploy path works before building product on top of it | Service `backlog-works` on Railway, `https://backlog.works` answers `HTTP/2 200`, `/healthz` returns `ok`; deploy path is `scripts/deploy.sh` (receipt in `docs/ops/handoff-2026-09-25.md`). Accepted by the Product Owner 2026-09-26. | Done | Team |
| V645. Licence decision | Decide what licence, if any, governs this repo | PO decided 2026-09-25: proprietary, all rights reserved (see LICENSE). | Done | Product Owner |
