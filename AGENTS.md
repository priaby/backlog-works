# backlog.works Agents Guide

This file is the top-level contract for agents working in this repo. It is
adapted from Crest's `AGENTS.md` (the product this repo was extracted from)
but keeps only what applies to a fresh, pre-alpha repository. Extend it as
the product grows — don't restore Crest-specific sections (deploy hosts,
brand assets, provider logos) unless this product actually needs them.

## File Ownership Map

- `README.md` — positioning, status, origin, license status.
- `AGENTS.md` — this file: workflow contract for agents. `CLAUDE.md` only
  imports it (`@AGENTS.md`); keep all guidance here.
- `.agents/skills/<name>/SKILL.md` — canonical task skills;
  `.claude/skills/<name>` are relative symlinks to them (Crest layout).
  `scripts/check.sh` fails if the two sets drift.
- `docs/product/backlog.md` — the product backlog in the product's own
  format (see below). Product Owner priority order = document order.
- `docs/ops/` — handoffs, infra notes, operational receipts;
  `docs/ops/README.md` indexes them, newest first.
- `docs/architecture.md` — event-driven modular monolith: blocks, import
  matrix, event catalogue, storage, rules, decisions log. Read before adding code; update in the same commit
  as any structural change.
- `src/backlogworks/` — the deployed service, one package with the blocks
  listed in `docs/architecture.md` section 2 (`config`, `events`,
  `backlog`, `github`, `auth`, `notify`, `local`, `landing`, `docs`, `web`).
  `tests/<block>/` — unittest per block. `Dockerfile`, `railway.json` —
  build and deploy config.
- `scripts/check.sh` — the repo gate (run before every commit and handoff);
  `scripts/check_backlog.py` — backlog format checker;
  `scripts/check_architecture.py` — import matrix, env access, size cap,
  root allowlist; `scripts/deploy.sh` — the only deploy path.

## Skills

Load the skill whose trigger matches the task, once, at the start:

| Skill | Use when |
|---|---|
| `backlog-works-report` | session start (takeover), any Product Owner report, session close handoff |
| `backlog-works-backlog` | reading, editing, reordering, or changing status in `docs/product/backlog.md`; picking the next item |
| `backlog-works-deploy` | deploying, verifying a release, checking Railway/domain status |
| `backlog-works-extraction` | porting code from Crest for J709 (Persist backlog changes to the repo), U695 (Board on the phone: status views, reorder controls, design foundations) and their tests |
| `backlog-works-secrets` | fetching `RAILWAY_PAT`, adding a Railway variable, documenting any credential |

This file's directives win over any skill. A skill never authorises an
external action (deploy, push, vault write) on its own.

## Session Workflow

1. Read this file, `docs/architecture.md`, the newest
   `docs/ops/handoff-*.md`, and `docs/product/backlog.md`. Run
   `scripts/check.sh`.
2. Re-verify live claims from the last handoff with a current command
   before repeating them (domain status, deploy state).
3. Work one item (see "One PBI in progress at a time"). Small commits with
   conventional subjects (`feat:`, `fix:`, `docs:`, `chore:`), gate green
   before each commit, push to `main` (no branch protection yet; a PR is
   optional for a single-person team and required once a reviewer exists).
4. Deploy only via `scripts/deploy.sh`, only a pushed `main` SHA.
5. Close with a handoff section and a three-part report
   (`backlog-works-report`).

## Product Owner Standing Directives

These generalise from Crest's Product Owner directives and apply from an
agent's first message in this repo, without being reminded:

- **Name every PBI in full.** Never a bare index; write the id
  with its title, e.g. "U695 (Board on the phone: status views, reorder controls, design foundations)" — look it up in
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
- **One PBI worked at a time.** Several items may be `In Progress` (the
  Sprint Backlog); the team works the highest one first and pulls the next
  only after it is merged and reported for acceptance, or parked with
  `Waiting on: <condition>` in its Status cell.
- **The team never creates Product Backlog Items on its own.** Work the
  Product Owner asks for happens inside the active item; findings and ideas
  are proposals in the report, and become PBIs only when the Product Owner
  says so.
- **Backlog document order is priority order.** `docs/product/backlog.md`'s
  document order is priority order; work the highest `In Progress` item.
  Never start a `Ready` or ordinary item; selection into the Sprint is the
  Product Owner's.
- **Model routing is the orchestrator's call, not the Product Owner's.**
  Route packets to models by difficulty and quota; never ask the Product
  Owner to pick a model.
- **No readiness claims without a receipt.** Don't say a step waits only on
  a Product Owner decision, or that a capability works, until the real path
  has been exercised end to end with current evidence.

## Infrastructure Facts

- **Hosting:** Railway. Production target is `backlog.works`.
- **Secrets:** live in Railway project variables, not repo files.
- **Bitwarden:** two secrets in Crest's Bitwarden Secrets Manager are
  relevant to this repo — name/UUID only, never the value, per Crest's
  Bitwarden secret-handling rule. `RAILWAY_API` (UUID
  `06e63f66-0e2e-4723-b2f7-b4d1006991bc`, added by the PO 2026-09-26) is a
  Railway **workspace-scope** token: `me` returns `Not Authorized`, but
  `workspace`, `projects`, `railwayDomainByName`, `railwayDomainDnsRecords`
  and the `railwayDomainDnsRecord{Create,Update,Delete}` mutations work
  (receipt: `docs/ops/handoff-2026-09-26.md`, session 5). Use it as a
  `Authorization: Bearer` header on `https://backboard.railway.com/graphql/v2`
  via curl (Python's default `urllib` user agent gets HTTP 403); the
  workspace id below is a required argument. It is the path for DNS
  changes on the Railway-managed `backlog.works` zone. The deploy token is
  `RAILWAY_PAT` (UUID `4852b697-a726-4c8b-99f4-b4d000db3493`). It is
  a Railway **project token** (`RAILWAY_TOKEN` env var, not
  `RAILWAY_API_TOKEN`), scoped to the project below only. It is read-mostly
  in most of the CLI (`railway link`, `railway project rename` — no such
  command exists — and other account-scope calls return `Unauthorized`),
  but service creation and deploy succeed when the project/service/
  environment are passed explicitly via CLI flags rather than relying on a
  local `railway link` state file.
- **Railway project:** name `marvelous-wisdom` (pre-existing, generic name
  — no CLI rename path exists for a project-scoped token; renaming needs an
  account-level PAT, left to the Product Owner if wanted), ID
  `a611baf5-ab5c-432f-9370-88dab8c378c7`, workspace "My Projects" (ID
  `fd88d265-ad97-4e65-96c2-f16bc43033b0`), environment `production` (ID
  `58c03d4e-9dd6-4ae1-97c7-caa5248699fe`).
- **Service:** name `backlog-works`, ID `d42bcadc-5c37-46b1-aee2-b6904d25b5b3`.
  Deployed from this repo's `Dockerfile` (`python:3.12-slim`, stdlib-only
  `python3 -m backlogworks`, `GET /` placeholder page, `GET /healthz` →
  `200 ok`).
  Generated domain: `https://backlog-works-production.up.railway.app`
  (confirmed `200`/`ok` on both routes). Startup note: `web/server.py`
  overrides `server_bind` to skip the reverse-DNS lookup that stalled boot
  by 5 s locally.
- **Custom domain:** `backlog.works` attached
  (`customDomainCreate` id `1a99d12f-c40c-41f1-a75b-0aae62b4d70a`). Railway
  returned a required CNAME (`backlog.works` → `3vtl6rr0.up.railway.app`)
  and an ownership-verification TXT host (`_railway-verify`). The domain
  was purchased through Railway's own registrar and DNS converged on its
  own: as of 2026-09-25 14:22 UTC `dig +short backlog.works` returns
  `69.46.46.108` and `curl -sI https://backlog.works` returns `HTTP/2 200`
  (receipt in `docs/ops/handoff-2026-09-25.md`).
- **Command pattern (hard rule — never print/echo/persist the token):**

  ```sh
  RAILWAY_TOKEN="$(cd /home/priaby/Projects/crest && python3 scripts/crest_bws.py get RAILWAY_PAT | tr -d '[:space:]')" \
    railway <command> --project a611baf5-ab5c-432f-9370-88dab8c378c7 \
    --service backlog-works --environment production
  ```

  Pass `--project`/`--service`/`--environment` explicitly on every call in
  this repo; do not depend on `railway link` (it fails `Unauthorized` for
  this project-scoped token even though direct-flag calls succeed).

- **Deploy only via `scripts/deploy.sh` from this checkout; never run
  `railway up` directly from another directory (incident 2026-09-25:
  Crest's Dockerfile got deployed to Railway — guard in place now).**
  The deploy script resolves the repo root, validates `railway.json` and
  `src/backlogworks/__main__.py` presence, fetches the token via BWS inline (never echoed
  or traced), passes all three scope flags explicitly, and polls the
  custom domain until `200` is reached or 6 minutes elapse, then also
  checks the generated domain's `/healthz`.

## The Backlog File

`docs/product/backlog.md` is the product backlog in the product's own
format: a markdown table whose rows begin `| <id>. ` in the table's
active section, columns `Item (PBI)`, `Core Job`, `Context`, `Status`,
`Driver`. An item id (PO decision 2026-09-26) is one uppercase letter
from `ABCDEFGHJKLMNPRSTUVWXYZ` plus three digits `100`-`999` (`K417`),
random, unique within the file, assigned at creation, never reused;
`scripts/new_id.py` mints one. No `PBI-` prefix, no type field (bugs
are not a separate section; a type field is a later product decision).
Two-tier status (PO decision 2026-09-26): an item is open or done
(`Done` in the cell closes it); an open item may carry a stage (`Ready`,
`In Progress`, or a custom word). Title at most 80 characters, Context
at most 280; the parser flags longer cells and the gate fails on them. Statuses (PO decision
2026-09-26, Scrum Guide grounded): empty = ordinary item; `Ready` = meets
the Definition of Ready, selectable in Sprint Planning; `In Progress` =
in the Sprint Backlog; `Done` = meets the Definition of Done, accepted.
Notes after `<br>` (`Sprint: S4`, `Waiting on: <condition>`); cancelled
rows are deleted. This format (and the row-reorder invariants a future
write path should enforce — same id set, same per-row cell count, only row
order changes) is inherited from Crest's `backlog_source.py` design; keep
compatible with it unless the Product Owner approves a format change.

## Editing Rules

- Run `scripts/check.sh` before every commit; it must print `CHECK PASS`.
- Keep docs concise, ASCII where practical. No secrets, tokens, passwords,
  or private personal data in repo docs — names and UUIDs only.
- **Licensing (PO decision 2026-09-25):** proprietary commercial product;
  public repo for visibility only; never add an OSS licence, OSS badges,
  or 'contributions welcome' copy.
