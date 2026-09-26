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
works the top `Planned` or `In Progress` row.

> [!info] Status legend
> `Candidate` — in the backlog, not yet scheduled.
> `Planned` — scheduled for the current Sprint.
> `In Progress` — actively being worked.
> `Review` — implemented, awaiting Product Owner acceptance.
> `Done` — accepted by the Product Owner.
> A blocked item keeps its status and adds `Waiting on: <condition>` after
> `<br>`. Cancelled items are deleted from the file; git history keeps them.

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| PBI-014. Deadline reminders by email | Never miss a delivery date while working on another job | Send one reminder 48h and one 4h before each deadline; opt out per project. Depends on PBI-009 (Transactional email provider) being accepted. | In Progress<br>Sprint: S4 | Team |
| PBI-011. Client portal download link | Let a client fetch the delivered files without an account | Signed, expiring link per delivery; download counted; link revocable from the job page. | Planned<br>Sprint: S4 | Team |
| PBI-015. Payment status on the job card | See at a glance which delivered jobs are still unpaid | Show invoice state (draft, sent, overdue, paid) on each job card; overdue in red after the due date. Pulls from PBI-010 (Invoice PDF). | Planned<br>Sprint: S4 | Team |
| PBI-016. Weekly workload view | Decide whether to accept a new job this week | Calendar strip with words-per-day capacity vs. committed words; red when over capacity. | Candidate | Team |
| PBI-017. CAT tool import (XLIFF 2.0) | Start a job from the file the agency already sent | Parse XLIFF 2.0, count words and segments, prefill the job; reject 1.2 with a clear message. | Candidate | Team |
| PBI-018. Glossary per client | Keep terminology consistent across jobs for the same client | Simple two-column glossary attached to a client; searchable from the job page. | Candidate | Team |
| PBI-019. Agency rate cards | Stop re-typing the same per-word rate | Rate card per client with per-language-pair rates; job total prefilled. | Candidate | Team |
| PBI-020. Mobile quick-accept | Accept a job offer from the phone in one tap | Push notification with word count and deadline; Accept creates the job with the rate card applied. | Candidate | Team |
| PBI-012. Two-factor sign-in | Protect client files behind more than a password | TOTP with recovery codes; required for accounts with client-portal links. | Planned<br>Waiting on: security review appointment (external, booked 2026-10-06) | Team |
| PBI-013. Export all data | Leave with everything, in a format another tool can read | ZIP with JSON + CSV per entity and all delivered files. | Review<br>Sprint: S3 | Team |
| PBI-009. Transactional email provider | Reach users reliably with account and reminder mail | Chose a provider; reminder mail follows user preferences, account/security mail is always sent; delivery webhook stored. | Done | Team |
| PBI-010. Invoice PDF | Invoice a delivered job in one click | One-page PDF with the agency's billing details, job lines, VAT line, IBAN; numbered sequence per year. | Done | Team |

## Bugs

- **BUG-2026-09-22-overdue-colour** — Surface: job card. Steps: create a
  job with an invoice due yesterday, open the list. Expected: red overdue
  badge. Actual: badge stays grey until the page is reloaded twice.
  Severity: low. Status: open.
