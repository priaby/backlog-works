# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import hashlib
import html
import unittest
from dataclasses import replace
from html.parser import HTMLParser
from unittest.mock import patch

from backlogworks.backlog import Bug, parse_backlog
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
        self.assertEqual(ids, list(backlog.ids) + [bug.id for bug in backlog.bugs])
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].payload["items"], len(backlog.items))

    def test_demo_event_hashes_exact_file_bytes(self):
        content = (b"# Example\r\n| PBI-001. Example | Job | Context | Ready | Team |\r\n")
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
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| PBI-001. <b>x</b> | j | c | Ready | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)
        self.assertNotIn("<b>x</b>", page)

    def test_view_membership_and_rank_follow_document_order(self):
        md = "\n".join(f"| PBI-{i:03}. Item {i} | job | context | {status} | Team |"
                       for i, status in enumerate(("", "Done", "Ready", "In Progress", "Unknown"), 1))
        page = render_board(parse_backlog(md), repo="r")
        rows = [attrs for _, attrs in Elements(page).elements if 'data-views' in attrs]
        self.assertEqual([r['data-views'].split() for r in rows],
                         [['all', 'open'], ['all', 'done'], ['all', 'open', 'ready'],
                          ['all', 'open', 'sprint'], ['all', 'open']])
        self.assertEqual([r['data-status'] for r in rows], ["", "Done", "Ready", "In Progress", "Unknown"])
        for rank in range(1, 6):
            self.assertIn(f'aria-label="Priority {rank}">{rank}</span>', page)

    def test_filter_options_preserve_first_seen_order_and_all_view_fallback(self):
        md = "\n".join(f"| PBI-{i:03}. Title | {job} | context | Ready | Team |"
                       for i, job in enumerate(('Zebra', 'all', 'Zebra', '', 'Alpha'), 1))
        page = render_board(parse_backlog(md), repo="r", board_path="/tenant/sample/")
        expected = '<option value="all">All core jobs</option><option value="0">Zebra</option>'
        expected += '<option value="1">all</option><option value="2"></option><option value="3">Alpha</option>'
        self.assertIn(expected, page)
        self.assertIn('href="/tenant/sample/backlog.md"', page)
        buttons = [a for t, a in Elements(page).elements if t == 'button']
        self.assertEqual([b['data-view'] for b in buttons], ['open', 'sprint', 'ready', 'done', 'bugs', 'all'])
        self.assertEqual([b['data-view'] for b in buttons if b['aria-pressed'] == 'true'], ['all'])
        self.assertTrue(all('disabled' in b for b in buttons))
        rows = [a for _, a in Elements(page).elements if 'data-views' in a]
        self.assertTrue(all('hidden' not in row for row in rows))

    def test_masthead_chips_waiting_bugs_and_only_code_markup(self):
        md = '# Title\n\nDescription `code`.\n\n'
        md += '| PBI-001. Title | Job | **literal** [link](url) `code` | Ready<br>Waiting on: review<br>Sprint: S4 | Team |\n'
        md += '\n## Bugs\n- **BUG-one** Broken `thing`\n'
        page = render_board(parse_backlog(md), repo="tenant")
        for fragment in ('class="eyebrow">tenant', '<h1>Title</h1>',
                         'Description <code>code</code>.', 'Source updated n/a',
                         'class="chip sprint">S4', 'class="pill">Waiting</span> review',
                         'data-views="bugs all"', 'Broken <code>thing</code>',
                         '**literal** [link](url) <code>code</code>'):
            self.assertIn(fragment, page)

    def test_all_source_fields_are_escaped_in_text_and_attributes(self):
        _, backlog = load_demo()
        payload = '<img src=x onerror="alert(1)">&\' </script> `code`'
        item = replace(backlog.items[0], title=payload, core_job=payload, context=payload,
                       status=payload, status_note='Waiting on: ' + payload, driver=payload)
        backlog = replace(backlog, title=payload, updated=payload, description=payload,
                          items=(item,), bugs=(Bug('BUG-"<bad>', payload),), problems=(payload,))
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
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| PBI-001. x | j | c |  | T |\n"
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
