# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import html
import unittest
from dataclasses import replace
from html.parser import HTMLParser

from backlogworks.backlog import parse_backlog
from backlogworks.config import Config
from backlogworks.events import Event, EventBus
from backlogworks.local import load_backlog
from backlogworks.web.board import render_board


class Elements(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.elements = []
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class BoardTests(unittest.TestCase):
    def test_local_renders_every_item_in_order_and_escapes(self):
        seen: list[Event] = []
        bus = EventBus()
        bus.subscribe("backlog.loaded", seen.append)
        _, backlog = load_backlog(Config(), bus)
        page = render_board(backlog, repo="local/x")
        positions = [page.index(f'id="{i}"') for i in backlog.ids]
        self.assertEqual(positions, sorted(positions))
        ids = [attrs['id'] for tag, attrs in Elements(page).elements if tag == 'article']
        self.assertEqual(ids, list(backlog.ids))
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].payload["items"], len(backlog.items))

    def test_html_is_escaped(self):
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| K417. <b>x</b> | j | c | Ready | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)
        self.assertNotIn("<b>x</b>", page)

    def test_rows_carry_id_and_status_no_data_views_and_ranks_follow_order(self):
        md = "\n".join(f"| K{100+i}. Item {i} | job | context | {status} | Team |"
                       for i, status in enumerate(("", "Done", "Ready", "In Progress", "Blocked"), 1))
        page = render_board(parse_backlog(md), repo="r")
        rows = [attrs for _, attrs in Elements(page).elements if 'data-id' in attrs]
        self.assertEqual([r['data-status'] for r in rows], ["", "Done", "Ready", "In Progress", "Blocked"])
        self.assertTrue(all('data-views' not in attrs for _, attrs in Elements(page).elements))
        for rank in range(1, 6):
            self.assertIn(f'aria-label="Priority {rank}">{rank}</span>', page)

    def test_selector_is_all_then_backlog_statuses_only_all_pressed(self):
        md = "\n".join(f"| K{100+i}. Item {i} | job | context | {status} | Team |"
                       for i, status in enumerate(("Done", "Blocked", "Ready"), 1))
        backlog = parse_backlog(md)
        page = render_board(backlog, repo="r")
        buttons = [a for t, a in Elements(page).elements if t == 'button' and 'data-view' in a]
        self.assertEqual([b.get('data-filter') for b in buttons[1:]], list(backlog.statuses))
        self.assertEqual(buttons[0]['data-view'], 'all')
        self.assertTrue(all(b['data-view'] == 'status' for b in buttons[1:]))
        self.assertEqual([b['aria-pressed'] for b in buttons], ['true'] + ['false'] * (len(buttons) - 1))
        self.assertTrue(all('disabled' in b for b in buttons))
        self.assertIn('Blocked', [b.get('data-filter') for b in buttons])
        self.assertNotIn('>Open<', page)
        self.assertNotIn('data-view="open"', page)

    def test_noscript_copy(self):
        _, backlog = load_backlog(Config())
        page = render_board(backlog, repo="r")
        self.assertIn('All entries are shown in file order. Enable JavaScript to switch views and preview reordering.',
                     page)

    def test_custom_status_pill_class_is_s_custom(self):
        md = "| K417. Item | job | context | Blocked | Team |"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn('class="pill s-custom"', page)

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
        _, backlog = load_backlog(Config())
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

    def test_ordinary_item_has_no_pill(self):
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| K417. x | j | c |  | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertNotIn('class="pill', page)

    def test_demo_route_is_gone(self):
        from backlogworks.web.server import App
        resp = App(Config(), EventBus()).dispatch("/demo")
        self.assertEqual(resp[0], 404)

    def test_bus_isolates_failing_handler(self):
        bus = EventBus()
        calls = []
        bus.subscribe("x", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        bus.subscribe("x", calls.append)
        bus.publish(Event("x"))
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
