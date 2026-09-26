# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Server-rendered, phone-first board. No JavaScript needed to read it."""

from __future__ import annotations

import html
import re

from backlogworks.backlog import STATUSES, Backlog, Item

_CODE_RE = re.compile(r"`([^`]+)`")
_PBI_RE = re.compile(r"\b(PBI-\d+[a-z]?)\b")

STATUS_CLASS = {
    "Ready": "s-ready",
    "In Progress": "s-progress",
    "Done": "s-done",
}

CSS = """
  :root { --ink:#1d1d1f; --muted:#6e6e73; --line:#e5e5ea; --bg:#f5f5f7; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--ink); }
  header { position: sticky; top:0; background:#fff; border-bottom:1px solid var(--line); padding:.8em 1em; }
  header h1 { font-size:1.05em; margin:0; }
  header small { color: var(--muted); }
  main { max-width: 42em; margin: 0 auto; padding: .8em; }
  .card { background:#fff; border:1px solid var(--line); border-radius:.9em; padding:.9em 1em; margin:.6em 0; }
  .card .top { display:flex; justify-content:space-between; gap:.6em; align-items:baseline; }
  .id { font-variant-numeric: tabular-nums; color: var(--muted); font-size:.85em; }
  .title { font-weight:600; margin:.1em 0 .3em; }
  .job { color:#333; margin:0 0 .4em; }
  .ctx { color: var(--muted); font-size:.9em; margin:0; }
  .meta { display:flex; flex-wrap:wrap; gap:.4em; margin-top:.6em; align-items:center; font-size:.8em; }
  .pill { border-radius:999px; padding:.15em .6em; font-weight:600; white-space:nowrap; }
  .s-ready{background:#e8f0fe;color:#1a4fbf} .s-progress{background:#e6f4ea;color:#1e7b3a}
  .s-done{background:#d9f2e0;color:#0f5a2b} .s-waiting{background:#fde8e8;color:#a12a2a}
  .s-unknown{background:#fde8e8;color:#a12a2a;outline:1px dashed #a12a2a}
  .intro { background:#fff; border:1px solid var(--line); border-radius:.9em; padding:1em 1.1em; margin:.6em 0 1em; }
  .intro h2 { margin:0 0 .3em; font-size:1.1em; } .intro p { margin:.3em 0; color:#333; } .intro ul { margin:.3em 0 0 1.1em; padding:0; color:#333; }
  .note { color: var(--muted); }
  .rank { color: var(--muted); font-size:.8em; }
  .problems { background:#fff4e5; border:1px solid #f5d29c; border-radius:.6em; padding:.6em .9em; font-size:.85em; }
  code { background: var(--bg); padding:0 .25em; border-radius:.3em; font-size:.92em; }
  footer { color: var(--muted); font-size:.8em; text-align:center; padding:1.5em; }
  .card.done { opacity:.7; }
"""


def _inline(text: str) -> str:
    out = html.escape(text)
    out = _CODE_RE.sub(r"<code>\1</code>", out)
    return out


def _card(rank: int, item: Item) -> str:
    extra = " done" if item.status == "Done" else ""
    if item.status == "":
        pill = ""
    else:
        pill = f'<span class="pill {STATUS_CLASS.get(item.status, "s-unknown")}">{html.escape(item.status)}</span>'
    if item.waiting_on:
        note = f'<span class="pill s-waiting">Waiting</span><span class="note">on {_inline(item.waiting_on)}</span>'
    else:
        note = f'<span class="note">{_inline(item.status_note)}</span>' if item.status_note else ""
    return (
        f'<article class="card{extra}" id="{html.escape(item.id)}">'
        f'<div class="top"><span class="id">{html.escape(item.id)}</span><span class="rank">#{rank}</span></div>'
        f'<div class="title">{_inline(item.title)}</div>'
        f'<p class="job">{_inline(item.core_job)}</p>'
        f'<p class="ctx">{_inline(item.context)}</p>'
        f'<div class="meta">{pill}{note}'
        f'<span class="note">Driver: {_inline(item.driver)}</span></div>'
        f"</article>"
    )


def render_board(backlog: Backlog, *, repo: str, subtitle: str = "", intro_html: str = "") -> str:
    """One engine for every backlog view: tenant boards, the demo, and the
    landing all call this. `intro_html` is trusted, pre-escaped chrome."""
    cards = "\n".join(_card(i + 1, item) for i, item in enumerate(backlog.items))
    counts = {s: sum(1 for i in backlog.items if i.status == s) for s in STATUSES if s}
    summary = " · ".join(f"{n} {s}" for s, n in counts.items() if n)
    problems = ""
    if backlog.problems:
        items = "".join(f"<li>{html.escape(p)}</li>" for p in backlog.problems)
        problems = f'<div class="problems"><strong>Format notes</strong><ul>{items}</ul></div>'
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
<header><h1>{html.escape(backlog.title)}</h1>
<small>{html.escape(repo)} · updated {html.escape(backlog.updated or "n/a")} · {html.escape(subtitle)}</small></header>
<main>
{intro_html}
{problems}
<p class="rank">{len(backlog.items)} items · {html.escape(summary)}</p>
{cards}
</main>
<footer>Rendered by backlog.works from a markdown file. Document order is priority order.</footer>
</body>
</html>
"""
