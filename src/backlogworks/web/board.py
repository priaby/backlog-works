# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""One server-rendered board for any parsed backlog, enhanced locally by JS."""

from __future__ import annotations

import html
import re

from backlogworks.backlog import Backlog, Bug, Item
from backlogworks.web.board_assets import CSS, SCRIPT

_CODE_RE = re.compile(r"`([^`]+)`")
_SPRINT_RE = re.compile(r"\bSprint:\s*([^,;\n]+)")
STATUS_CLASS = {"Ready": "s-ready", "In Progress": "s-progress", "Done": "s-done"}
VIEWS = ("Open", "Sprint", "Ready", "Done", "Bugs", "All")


def _inline(text: str) -> str:
    """Escape first; backtick code spans are the only supported markup."""
    return _CODE_RE.sub(r"<code>\1</code>", html.escape(text))


def _card(rank: int, item: Item) -> str:
    views = ["all"]
    if item.status != "Done":
        views.append("open")
    if item.status in STATUS_CLASS:
        views.append({"Ready": "ready", "In Progress": "sprint", "Done": "done"}[item.status])
    pill = (f'<span class="pill {STATUS_CLASS.get(item.status, "s-unknown")}">'
            f'{_inline(item.status)}</span>') if item.status else ""
    notes = item.status_note.replace("<br>", "\n")
    sprint = _SPRINT_RE.search(notes)
    sprint_chip = f'<span class="chip sprint">{_inline(sprint[1].strip())}</span>' if sprint else ""
    waiting = ""
    if item.waiting_on:
        condition = item.waiting_on.split("<br>", 1)[0]
        waiting = f'<p class="waiting"><span class="pill">Waiting</span> {_inline(condition)}</p>'
    return (
        f'<div class="card-row" data-views="{" ".join(views)}" '
        f'data-status="{html.escape(item.status)}" data-job="{html.escape(item.core_job)}">'
        f'<span class="rank" aria-label="Priority {rank}">{rank}</span>'
        f'<article class="card" id="{html.escape(item.id)}">'
        f'<h2 class="item-title"><span class="item-id">{_inline(item.id)}.</span> {_inline(item.title)}</h2>'
        f'<div class="meta">{pill}<span class="chip">{_inline(item.core_job)}</span>{sprint_chip}</div>'
        f'{waiting}<p class="context">{_inline(item.context)}</p>'
        '<!-- Reorder controls belong here when the write path is available. -->'
        '</article></div>'
    )


def _bug_card(bug: Bug) -> str:
    return (
        '<div class="card-row bug-row" data-views="bugs all" data-job="">'
        f'<article class="card" id="{html.escape(bug.id)}">'
        f'<h2 class="item-title item-id">{_inline(bug.id)}</h2>'
        f'<p class="context">{_inline(bug.text)}</p></article></div>'
    )


def render_board(backlog: Backlog, *, repo: str, subtitle: str = "",
                 intro_html: str = "", board_path: str = "") -> str:
    """Render escaped source values. Only intro_html is trusted chrome.

    board_path is the local board route, e.g. /teams/example; its markdown
    lives at <board_path>/backlog.md. No JS is needed to read the All view.
    """
    cards = "\n".join(_card(i + 1, item) for i, item in enumerate(backlog.items))
    bugs = "\n".join(_bug_card(bug) for bug in backlog.bugs)
    buttons = "\n".join(
        f'<button type="button" data-view="{view.lower()}" '
        f'aria-pressed="{str(view == "All").lower()}" disabled>{view}</button>'
        for view in VIEWS
    )
    # Numeric values keep the all-jobs sentinel distinct from every source value,
    # including an empty Core Job or a literal "all".
    jobs = dict.fromkeys(item.core_job for item in backlog.items)
    options = "".join(f'<option value="{i}">{html.escape(job)}</option>'
                      for i, job in enumerate(jobs))
    problems = ""
    if backlog.problems:
        notes = "".join(f"<li>{_inline(p)}</li>" for p in backlog.problems)
        problems = f'<aside class="problems"><strong>Format notes</strong><ul>{notes}</ul></aside>'
    source = html.escape("/" + board_path.strip("/") + "/backlog.md" if board_path.strip("/") else "/backlog.md")
    total = len(backlog.items) + len(backlog.bugs)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(backlog.title)} · backlog.works</title>
<style>{CSS}</style>
</head>
<body>
<main>
{intro_html}
<section id="board" aria-label="Backlog board">
<header class="masthead">
<p class="eyebrow">{_inline(repo)}</p>
<h1>{_inline(backlog.title)}</h1>
<p class="description">{_inline(backlog.description)}</p>
<div class="source-line"><span>Source updated {_inline(backlog.updated or "n/a")}</span>
<a href="{source}">Open Markdown source</a></div>
<p class="subtitle">{_inline(subtitle)}</p>
</header>
{problems}
<div class="view-switch" role="group" aria-label="Show backlog view">{buttons}</div>
<p id="view-count" class="count" role="status" aria-live="polite">All · {total} entries</p>
<details class="filters">
<summary>Filter</summary>
<div class="filter-fields">
<label>Core Job<select id="job-filter" disabled><option value="all">All core jobs</option>{options}</select></label>
<label>Search<input id="search" type="search" placeholder="Search id or title" disabled></label>
</div>
</details>
<noscript><p class="count">All entries are shown. Enable JavaScript to switch views and filter.</p></noscript>
<div id="cards">{cards}{bugs}</div>
<p id="empty-state" class="empty" hidden>No matching items.</p>
</section>
</main>
<footer>Rendered by backlog.works from a markdown file. Document order is priority order.</footer>
<script>{SCRIPT}</script>
</body>
</html>
"""
