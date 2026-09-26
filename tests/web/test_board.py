# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import hashlib
import html
import unittest
from dataclasses import replace
from html.parser import HTMLParser
from unittest.mock import patch

from backlogworks.backlog import parse_backlog
from backlogworks.demo import load_demo
from backlogworks.demo import source
from backlogworks.events import Event, EventBus
from backlogworks.web.board import render_board


class Elements(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.elements = []
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class BoardTests(unittest.TestCase):
    def test_demo_renders_every_item_in_order_and_escapes(self):
        seen: list[Event] = []
        bus = EventBus()
        bus.subscribe("backlog.loaded", seen.append)
        _, backlog = load_demo(bus)
        page = render_board(backlog, repo="demo/x")
        positions = [page.index(f'id="{i}"') for i in backlog.ids]
        self.assertEqual(positions, sorted(positions))
        ids = [attrs['id'] for tag, attrs in Elements(page).elements if tag == 'article']
        self.assertEqual(ids, list(backlog.ids))
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].payload["items"], len(backlog.items))

    def test_demo_event_hashes_exact_file_bytes(self):
        content = (b"# Example\r\n| K417. Example | Job | Context | Ready | Team |\r\n")
        bus = EventBus()
        seen = []
        bus.subscribe("backlog.loaded", seen.append)
        with patch.object(source, "_FILE") as file:
            file.read_bytes.return_value = content
            markdown, backlog = load_demo(bus)
        self.assertEqual(markdown.encode("utf-8"), content)
        self.assertEqual(seen[0].payload, {
            "source": "packaged", "sha": hashlib.sha1(content).hexdigest(),
            "items": len(backlog.items), "problems": len(backlog.problems),
        })
        self.assertEqual(seen[0].repo, source.DEMO_REPO)

    def test_html_is_escaped(self):
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| K417. <b>x</b> | j | c | Ready | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)
        self.assertNotIn("<b>x</b>", page)

    def test_view_membership_and_rank_follow_document_order(self):
        md = "\n".join(f"| K{100+i}. Item {i} | job | context | {status} | Team |"
                       for i, status in enumerate(("", "Done", "Ready", "In Progress", "Unknown"), 1))
        page = render_board(parse_backlog(md), repo="r")
        rows = [attrs for _, attrs in Elements(page).elements if 'data-views' in attrs]
        self.assertEqual([r['data-views'].split() for r in rows],
                         [['all', 'open'], ['all', 'done'], ['all', 'open', 'ready'],
                          ['all', 'open'], ['all', 'open']])
        self.assertEqual([r['data-status'] for r in rows], ["", "Done", "Ready", "In Progress", "Unknown"])
        for rank in range(1, 6):
            self.assertIn(f'aria-label="Priority {rank}">{rank}</span>', page)

    def test_four_views_and_all_view_fallback(self):
        _, backlog = load_demo()
        page = render_board(backlog, repo="r", board_path="/tenant/sample/")
        self.assertIn('href="/tenant/sample/backlog.md"', page)
        buttons = [a for t, a in Elements(page).elements if t == 'button']
        self.assertEqual([b['data-view'] for b in buttons], ['open', 'ready', 'done', 'all'])
        self.assertEqual([b['data-view'] for b in buttons if b['aria-pressed'] == 'true'], ['all'])
        self.assertTrue(all('disabled' in b for b in buttons))
        rows = [a for _, a in Elements(page).elements if 'data-views' in a]
        self.assertTrue(all('hidden' not in row for row in rows))
        self.assertIn('All entries are shown. Enable JavaScript to switch views.', page)
        self.assertIn("let view = 'open'", page)

    def test_filter_count_empty_state_and_bug_markup_are_absent(self):
        _, backlog = load_demo()
        page = render_board(backlog, repo="r")
        for fragment in ('view-count', 'job-filter', 'id="search"',
                         'bug-row', 'data-view="bugs"', 'data-view="sprint"',
                         'Reorder controls', 'repeat(6,'):
            self.assertNotIn(fragment, page)
        elements = Elements(page).elements
        self.assertFalse(any(tag in ('details', 'select', 'input') for tag, _ in elements))
        self.assertEqual(sum(tag == 'button' for tag, _ in elements), 4)
        self.assertIn('repeat(4,minmax', page)

    def test_masthead_chips_waiting_and_only_code_markup(self):
        md = '# Title\n\nDescription `code`.\n\n'
        md += '| K417. Title | Job | **literal** [link](url) `code` | Ready<br>Waiting on: review<br>Sprint: S4 | Team |\n'
        page = render_board(parse_backlog(md), repo="tenant")
        for fragment in ('class="eyebrow">tenant', '<h1>Title</h1>',
                         'Description <code>code</code>.', 'Source updated n/a',
                         'class="chip sprint">S4', 'class="pill">Waiting</span> review',
                         '**literal** [link](url) <code>code</code>'):
            self.assertIn(fragment, page)

    def test_all_source_fields_are_escaped_in_text_and_attributes(self):
        _, backlog = load_demo()
        payload = '<img src=x onerror="alert(1)">&\' </script> `code`'
        item = replace(backlog.items[0], title=payload, core_job=payload, context=payload,
                       status=payload, status_note='Waiting on: ' + payload, driver=payload)
        backlog = replace(backlog, title=payload, updated=payload, description=payload,
                          items=(item,), problems=(payload,))
        page = render_board(backlog, repo=payload, subtitle=payload)
        self.assertNotIn(payload, page)
        self.assertIn(html.escape(payload), page)
        self.assertIn('&lt;/script&gt; <code>code</code>', page)
        elements = Elements(page).elements
        self.assertEqual(sum(tag == 'script' for tag, _ in elements), 1)
        self.assertFalse(any(tag == 'img' or 'onerror' in attrs for tag, attrs in elements))
        row = next(attrs for _, attrs in elements if 'data-status' in attrs)
        self.assertEqual(row['data-job'], payload)
        self.assertEqual(row['data-status'], payload)

    def test_ordinary_item_has_no_pill_and_demo_redirects(self):
        from backlogworks.config import Config
        from backlogworks.web.server import App
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| K417. x | j | c |  | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertNotIn('class="pill', page)
        resp = App(Config(), EventBus()).dispatch("/demo")
        self.assertEqual(resp[0], 301)
        self.assertEqual(resp[3]["Location"], "/")

    def test_bus_isolates_failing_handler(self):
        bus = EventBus()
        calls = []
        bus.subscribe("x", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        bus.subscribe("x", calls.append)
        bus.publish(Event("x"))
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
