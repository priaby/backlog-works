# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""One server-rendered board for any parsed backlog, enhanced locally by JS."""

from __future__ import annotations

import html
import re
import zlib

from backlogworks.backlog import Backlog, Item
from backlogworks.web.board_assets import CSS, SCRIPT

_CODE_RE = re.compile(r"`([^`]+)`")
_SPRINT_RE = re.compile(r"\bSprint:\s*([^,;\n]+)")

_MOVES = (("up", "Move up", "M6 15l6-6 6 6"),
          ("down", "Move down", "M6 9l6 6 6-6"),
          ("top", "Move to top", "M6 5h12M6 18l6-6 6 6"))

_VIEWS = (("open", "Open"), ("progress", "In progress"), ("done", "Done"), ("all", "All"))
_DEFAULT_VIEW = "open"


def _tone(status: str) -> str:
    """Map a status to a docs/design-system.md tone name. Stable across
    processes: `In Progress`/`Ready`/`Done` are fixed hues, empty is
    neutral, anything else picks one of 4 hues from a hash of the text."""
    if status == "In Progress":
        return "progress"
    if status == "Ready":
        return "ready"
    if status == "Done":
        return "done"
    if not status:
        return "neutral"
    return f"h{zlib.crc32(status.encode()) % 4 + 1}"


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
            f'<button type="button" class="bw-button bw-button--icon" data-move="{kind}" '
            f'aria-label="{label}" title="{label}" disabled{edge_attr}>{_svg(path)}</button>'
        )
    return (f'<div class="bw-controls" role="group" aria-label="Reorder {html.escape(item.id)}">'
            f'{"".join(buttons)}</div>')


def _card(rank: int, item: Item, *, is_first: bool, is_last: bool) -> str:
    tone = _tone(item.status)
    custom = " bw-pill--custom" if tone.startswith("h") else ""
    pill = (f'<span class="bw-pill bw-tone-{tone}{custom}">'
            f'{_inline(item.status)}</span>') if item.status else ""
    notes = item.status_note.replace("<br>", "\n")
    sprint = _SPRINT_RE.search(notes)
    sprint_chip = f'<span class="bw-chip bw-chip--sprint">{_inline(sprint[1].strip())}</span>' if sprint else ""
    waiting = ""
    if item.waiting_on:
        condition = item.waiting_on.split("<br>", 1)[0]
        waiting = (f'<p class="bw-card__waiting"><span class="bw-pill bw-tone-waiting">Waiting</span> '
                   f'{_inline(condition)}</p>')
    return (
        f'<div class="bw-card-row" data-id="{html.escape(item.id)}" '
        f'data-state="{item.state}" data-stage="{html.escape(item.stage)}" tabindex="-1">'
        f'<span class="bw-rank" aria-label="Priority {rank}">{rank}</span>'
        f'<article class="bw-card bw-tone-{tone}" id="{html.escape(item.id)}">'
        f'<h2 class="bw-card__title"><span class="bw-card__id">{_inline(item.id)}.</span> {_inline(item.title)}</h2>'
        f'<div class="bw-card__meta">{pill}<span class="bw-chip">{_inline(item.core_job)}</span>{sprint_chip}</div>'
        f'{waiting}<p class="bw-card__context">{_inline(item.context)}</p>'
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
    buttons = "\n".join(
        f'<button type="button" class="bw-segmented__option" data-view="{view}" '
        f'aria-pressed="{"true" if view == _DEFAULT_VIEW else "false"}" disabled>{_inline(label)}</button>'
        for view, label in _VIEWS
    )
    problems = ""
    if backlog.problems:
        notes = "".join(f"<li>{_inline(p)}</li>" for p in backlog.problems)
        problems = f'<aside class="bw-notice bw-notice--warn"><strong>Format notes</strong><ul>{notes}</ul></aside>'
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
<header class="bw-masthead">
<p class="bw-masthead__eyebrow">{_inline(repo)}</p>
<h1>{_inline(backlog.title)}</h1>
<p class="bw-masthead__description">{_inline(backlog.description)}</p>
<div class="bw-masthead__source"><span>Source updated {_inline(backlog.updated or "n/a")}</span>
<a href="{source}">Open Markdown source</a></div>
<p class="bw-masthead__subtitle">{_inline(subtitle)}</p>
</header>
{problems}
<div class="bw-segmented" role="group" aria-label="Show backlog view">{buttons}</div>
<div id="order-status" class="bw-notice" hidden><p role="status">Order changed in this browser only. Saving arrives with sign-in.</p><button type="button" id="order-reset" class="bw-button bw-button--quiet bw-button--sm">Reset</button></div>
<noscript><p class="bw-notice">All entries are shown in file order. Enable JavaScript to switch views and preview reordering.</p></noscript>
<div id="cards" class="bw-card-list">{cards}</div>
<p id="empty-state" class="bw-empty" hidden>Nothing in this view.</p>
</section>
</main>
<footer>Rendered by backlog.works from a markdown file. Document order is priority order.</footer>
<script>{SCRIPT}</script>
</body>
</html>
"""
