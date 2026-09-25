---
name: backlog-works-extraction
description: Port backlog-board code from the Crest repository into backlog.works (PBI-001 Extract backlog source module, PBI-002 Extract renderer/board, and their tests). Use when reading Crest source as a porting reference.
---

# Porting from Crest

Crest is checked out at `/home/priaby/Projects/crest` (private repo; read it
as reference, never copy its brand, accounts, or secrets handling). The
authoritative survey is Crest's
`artifacts/checks/backlog-works-extraction-inventory-2026-09-25.md`
(git-ignored there; if it is gone, re-derive from the source paths below).

## What to port, and its verdict

| Crest path | Verdict | Notes |
|---|---|---|
| `src/crest/infrastructure/backlog_source.py` (355 lines) | portable, small changes | GitHub Contents API read with 60s cache + ETag, `validate_reorder`/`apply_reorder`, PUT commit to `main`. Replace hardcoded owner/repo/path/committer and the `/app/admin-content` fallback with config. |
| `scripts/test_crest_backlog_source.py` (393 lines) | portable, small changes | Patches `urllib.request.urlopen`; port the `backlog_source` cases, drop the Crest session fixtures. |
| `src/crest/infrastructure/admin_content.py` (123 lines) | portable as technique | Inlines the markdown into the board HTML and patches one `fetch()` by exact string; needs our own board asset to patch. |
| `scripts/test_crest_admin_content.py` (107 lines) | portable as-is | |
| `docs/product/backlog-board.html` (1,148 lines) | portable, small changes | Markdown-table-to-cards logic is generic; strip Crest CSS/JS links and topbar; new unbranded design (PBI-006 Brand and landing page decides the look). |
| `src/crest/api/admin.py` (362 lines), `crest_analytics_api.py` admin routes (~90 lines) | rewrite | Keep the HTTP shape (hidden 404, CSRF = HMAC of session token, Origin allow-list, reorder body validation, 409 on stale `base_sha`); replace every `access.*` call with this product's own session (PBI-003 Standalone sign-in) or API key (PBI-004 API key for agents). |
| `scripts/test_crest_admin.py`, `assets/crest-email-code-challenge.*`, `scripts/check-crest-architecture.py` | spec only | Read for required behaviour; do not lift code. |

## Where ported code lands

`docs/architecture.md` section 3 is the map; `scripts/check_architecture.py`
enforces it. Crest's `backlog_source.py` splits in two here: the pure
parse/validate/reorder functions go to `src/backlogworks/backlog/`, the
Contents API client to `src/backlogworks/github/`. `admin_content.py` and
the board asset go to `src/backlogworks/web/` (asset under `web/assets/`).
Nothing from Crest's `admin.py` auth lands anywhere but as a spec for
`src/backlogworks/auth/`. Tests go to `tests/<block>/`.

## Rules while porting

- Stdlib only stays the default (`urllib`, `json`, `re`, `hmac`, `secrets`,
  `threading`). Adding a dependency is a proposal to the Product Owner.
- Preserve the format contract in
  `.agents/skills/backlog-works-backlog/SKILL.md`; `scripts/check_backlog.py`
  is the local mirror of what the ported parser must accept.
- The write path commits straight to `main` via the GitHub Contents API
  with optimistic concurrency on the file `sha`; keep that shape and its
  validation, and keep the single-file blast radius argument in the code
  comments.
- No Crest identifiers may survive: grep the ported files for `crest`,
  `Crest`, `priaby/crest`, `notify@`, `/app/admin-content`, `__CREST_`
  before opening the PR. Name the window global and env vars after this
  product.
- Port tests in the same commit as the module; run them with
  `python3 -m unittest discover -s tests` and wire that into
  `scripts/check.sh` when the first test lands.
- Crest's files carry no licence headers; add this repo's proprietary
  notice (see `LICENSE`) as a one-line header on new source files.
