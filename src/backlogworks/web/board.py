# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""One server-rendered board for any parsed backlog, enhanced locally by JS."""

from __future__ import annotations

import html
import re

from backlogworks.backlog import Backlog, Item
from backlogworks.web.board_assets import CSS, SCRIPT

_CODE_RE = re.compile(r"`([^`]+)`")
_SPRINT_RE = re.compile(r"\bSprint:\s*([^,;\n]+)")
STATUS_CLASS = {"Ready": "s-ready", "In Progress": "s-progress", "Done": "s-done"}

_MOVES = (("up", "Move up", "M6 15l6-6 6 6"),
          ("down", "Move down", "M6 9l6 6 6-6"),
          ("top", "Move to top", "M6 5h12M6 18l6-6 6 6"))


def _inline(text: str) -> str:
    """Escape first; backtick code spans are the only supported markup."""
    return _CODE_RE.sub(r"<code>\1</code>", html.escape(text))


def _svg(path: str) -> str:
    return (f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round"><path d="{path}"/></svg>')


def _controls(item: Item, *, is_first: bool, is_last: bool) -> str:
    edges = {"up": is_first, "down": is_last, "top": is_first}
    buttons = []
    for kind, label, path in _MOVES:
        edge_attr = " data-edge" if edges[kind] else ""
        buttons.append(
            f'<button type="button" class="move" data-move="{kind}" '
            f'aria-label="{label}" title="{label}" disabled{edge_attr}>{_svg(path)}</button>'
        )
    return (f'<div class="card-controls" role="group" aria-label="Reorder {html.escape(item.id)}">'
            f'{"".join(buttons)}</div>')


def _card(rank: int, item: Item, *, is_first: bool, is_last: bool) -> str:
    status_class = STATUS_CLASS.get(item.status, "s-custom")
    pill = (f'<span class="pill {status_class}">'
            f'{_inline(item.status)}</span>') if item.status else ""
    notes = item.status_note.replace("<br>", "\n")
    sprint = _SPRINT_RE.search(notes)
    sprint_chip = f'<span class="chip sprint">{_inline(sprint[1].strip())}</span>' if sprint else ""
    waiting = ""
    if item.waiting_on:
        condition = item.waiting_on.split("<br>", 1)[0]
        waiting = f'<p class="waiting"><span class="pill">Waiting</span> {_inline(condition)}</p>'
    return (
        f'<div class="card-row" data-id="{html.escape(item.id)}" '
        f'data-status="{html.escape(item.status)}" data-job="{html.escape(item.core_job)}">'
        f'<span class="rank" aria-label="Priority {rank}">{rank}</span>'
        f'<article class="card" id="{html.escape(item.id)}">'
        f'<h2 class="item-title"><span class="item-id">{_inline(item.id)}.</span> {_inline(item.title)}</h2>'
        f'<div class="meta">{pill}<span class="chip">{_inline(item.core_job)}</span>{sprint_chip}</div>'
        f'{waiting}<p class="context">{_inline(item.context)}</p>'
        f'{_controls(item, is_first=is_first, is_last=is_last)}'
        '</article></div>'
    )


def render_board(backlog: Backlog, *, repo: str, subtitle: str = "",
                 intro_html: str = "", board_path: str = "") -> str:
    """Render escaped source values. Only intro_html is trusted chrome.

    board_path is the local board route, e.g. /teams/example; its markdown
    lives at <board_path>/backlog.md. No JS is needed to read the All view.
    """
    n = len(backlog.items)
    cards = "\n".join(_card(i + 1, item, is_first=(i == 0), is_last=(i == n - 1))
                      for i, item in enumerate(backlog.items))
    all_button = '<button type="button" data-view="all" aria-pressed="true" disabled>All</button>'
    status_buttons = "\n".join(
        f'<button type="button" data-view="status" data-filter="{html.escape(s)}" '
        f'aria-pressed="false" disabled>{_inline(s)}</button>'
        for s in backlog.statuses
    )
    buttons = "\n".join((all_button, status_buttons))
    problems = ""
    if backlog.problems:
        notes = "".join(f"<li>{_inline(p)}</li>" for p in backlog.problems)
        problems = f'<aside class="problems"><strong>Format notes</strong><ul>{notes}</ul></aside>'
    source = html.escape("/" + board_path.strip("/") + "/backlog.md" if board_path.strip("/") else "/backlog.md")
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
<div id="order-status" class="order-status" hidden><p role="status">Order changed in this browser only. Saving arrives with sign-in.</p><button type="button" id="order-reset">Reset</button></div>
<noscript><p>All entries are shown in file order. Enable JavaScript to switch views and preview reordering.</p></noscript>
<div id="cards">{cards}</div>
<p id="empty-state" class="empty" hidden>Nothing in this view.</p>
</section>
</main>
<footer>Rendered by backlog.works from a markdown file. Document order is priority order.</footer>
<script>{SCRIPT}</script>
</body>
</html>
"""
