---
title: "Lighthouse Product Backlog"
doc_type: planning
status: active
owners: ["Product Owner"]
tags: ["backlog", "demo"]
updated: 2026-09-26
---

# Lighthouse Product Backlog

Lighthouse is a fictitious product used to demonstrate backlog.works: a
small app that helps freelance translators track deadlines, deliver files,
and get paid. Every item below is invented. Document order is priority
order; the Product Owner orders this table from a phone, the agentic team
works the `In Progress` rows of the current Sprint.

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
> Notes go after `<br>`: `Sprint: S4`, `Waiting on: <condition>`. An item
> that did not get Done "returns to the Product Backlog" by dropping its
> status. Cancelled items are deleted; git history keeps them.
> Item ids are one letter plus three digits (`K417`), assigned at creation, never reused.

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| U611. Deadline reminders by email | Never miss a delivery date while working on another job | Send one reminder 48h and one 4h before each deadline; opt out per project. Depends on S376 (Transactional email provider) being accepted. | In Progress<br>Sprint: S4 | Team |
| D508. Client portal download link | Let a client fetch the delivered files without an account | Signed, expiring link per delivery; download counted; link revocable from the job page. | In Progress<br>Sprint: S4 | Team |
| G869. Payment status on the job card | See at a glance which delivered jobs are still unpaid | Show invoice state (draft, sent, overdue, paid) on each job card; overdue in red after the due date. Pulls from J440 (Invoice PDF). | In Progress<br>Sprint: S4 | Team |
| R843. Weekly workload view | Decide whether to accept a new job this week | Calendar strip with words-per-day capacity vs. committed words; red when over capacity. | Ready | Team |
| U467. CAT tool import (XLIFF 2.0) | Start a job from the file the agency already sent | Parse XLIFF 2.0, count words and segments, prefill the job; reject 1.2 with a clear message. | Ready | Team |
| Z733. Glossary per client | Keep terminology consistent across jobs for the same client | Simple two-column glossary attached to a client; searchable from the job page. |  | Team |
| J651. Agency rate cards | Stop re-typing the same per-word rate | Rate card per client with per-language-pair rates; job total prefilled. |  | Team |
| F511. Mobile quick-accept | Accept a job offer from the phone in one tap | Push notification with word count and deadline; Accept creates the job with the rate card applied. |  | Team |
| C826. Two-factor sign-in | Protect client files behind more than a password | TOTP with recovery codes; required for accounts with client-portal links. | Ready<br>Waiting on: security review appointment (external, booked 2026-10-06) | Team |
| D347. Export all data | Leave with everything, in a format another tool can read | ZIP with JSON + CSV per entity and all delivered files. | In Progress<br>Sprint: S3, awaiting acceptance | Team |
| S376. Transactional email provider | Reach users reliably with account and reminder mail | Chose a provider; reminder mail follows user preferences, account/security mail is always sent; delivery webhook stored. | Done | Team |
| J440. Invoice PDF | Invoice a delivered job in one click | One-page PDF with the agency's billing details, job lines, VAT line, IBAN; numbered sequence per year. | Done | Team |
