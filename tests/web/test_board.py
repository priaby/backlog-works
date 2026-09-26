# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import html
import re
import unittest
from dataclasses import replace
from html.parser import HTMLParser

from backlogworks.backlog import parse_backlog
from backlogworks.config import Config
from backlogworks.events import Event, EventBus
from backlogworks.local import load_backlog
from backlogworks.web.board import render_board
from backlogworks.web.board_assets import SCRIPT


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

    def test_rows_carry_state_and_stage_and_ranks_follow_order(self):
        md = "\n".join(f"| K{100+i}. Item {i} | job | context | {status} | Team |"
                       for i, status in enumerate(("", "Done", "Ready", "In Progress", "Blocked"), 1))
        page = render_board(parse_backlog(md), repo="r")
        rows = [attrs for _, attrs in Elements(page).elements if 'data-id' in attrs]
        self.assertEqual([r['data-state'] for r in rows], ["open", "done", "open", "open", "open"])
        self.assertEqual([r['data-stage'] for r in rows], ["", "", "Ready", "In Progress", "Blocked"])
        self.assertTrue(all('data-status' not in attrs for _, attrs in Elements(page).elements))
        self.assertTrue(all('data-job' not in attrs for _, attrs in Elements(page).elements))
        self.assertTrue(all('data-views' not in attrs for _, attrs in Elements(page).elements))
        self.assertTrue(all(r.get('tabindex') == '-1' for r in rows))
        for rank in range(1, 6):
            self.assertIn(f'aria-label="Priority {rank}">{rank}</span>', page)

    def test_segmented_has_four_fixed_options_open_pressed(self):
        expected = [("open", "true", "Open"), ("progress", "false", "In progress"),
                    ("done", "false", "Done"), ("all", "false", "All")]
        pattern = (r'<button type="button" class="bw-segmented__option" data-view="([a-z]+)" '
                   r'aria-pressed="(true|false)" disabled>([^<]+)</button>')
        for statuses in (("Blocked", "Ready"), ("Done",)):
            md = "\n".join(f"| K{100+i}. Item {i} | job | context | {status} | Team |"
                           for i, status in enumerate(statuses, 1))
            page = render_board(parse_backlog(md), repo="r")
            self.assertEqual(re.findall(pattern, page), expected)
            self.assertNotIn('data-filter', page)
            self.assertNotIn('>Blocked</button>', page)

    def test_script_filters_on_state_and_stage(self):
        self.assertIn("r.dataset.state === 'open'", SCRIPT)
        self.assertIn("r.dataset.state === 'done'", SCRIPT)
        self.assertIn("r.dataset.stage === 'In Progress'", SCRIPT)
        self.assertNotIn("dataset.status", SCRIPT)
        self.assertNotIn("dataset.filter", SCRIPT)

    def test_card_controls_disabled_with_correct_edges(self):
        md = "\n".join(f"| K{100+i}. Item {i} | job | context | Ready | Team |" for i in range(1, 4))
        page = render_board(parse_backlog(md), repo="r")
        rows = [a for t, a in Elements(page).elements if t == 'div' and 'data-id' in a]
        self.assertEqual(len(rows), 3)
        move_buttons = [a for t, a in Elements(page).elements if t == 'button' and 'data-move' in a]
        self.assertEqual(len(move_buttons), 9)
        self.assertTrue(all('disabled' in b for b in move_buttons))
        labels = {'up': 'Move up', 'down': 'Move down', 'top': 'Move to top'}
        for b in move_buttons:
            self.assertEqual(b['aria-label'], labels[b['data-move']])
        first_three = move_buttons[0:3]
        middle_three = move_buttons[3:6]
        last_three = move_buttons[6:9]
        self.assertIn('data-edge', first_three[0])  # up
        self.assertNotIn('data-edge', first_three[1])  # down
        self.assertIn('data-edge', first_three[2])  # top
        self.assertTrue(all('data-edge' not in b for b in middle_three))
        self.assertNotIn('data-edge', last_three[0])  # up
        self.assertIn('data-edge', last_three[1])  # down
        self.assertNotIn('data-edge', last_three[2])  # top

    def test_single_row_backlog_gets_data_edge_on_all_three(self):
        md = "| K417. Item | job | context | Ready | Team |"
        page = render_board(parse_backlog(md), repo="r")
        move_buttons = [a for t, a in Elements(page).elements if t == 'button' and 'data-move' in a]
        self.assertEqual(len(move_buttons), 3)
        self.assertTrue(all('data-edge' in b for b in move_buttons))

    def test_order_status_and_reset_and_empty_state_present(self):
        _, backlog = load_backlog(Config())
        page = render_board(backlog, repo="r")
        self.assertIn('<div id="order-status" class="bw-notice" hidden>', page)
        self.assertIn('Order changed in this browser only. Saving arrives with sign-in.', page)
        self.assertIn('<button type="button" id="order-reset" class="bw-button bw-button--quiet bw-button--sm">Reset</button>', page)
        self.assertIn('<p id="empty-state" class="bw-empty" hidden>Nothing in this view.</p>', page)

    def test_persist_order_hook_present_single_script_no_inline_handlers(self):
        _, backlog = load_backlog(Config())
        page = render_board(backlog, repo="r")
        self.assertIn('function persistOrder(ids)', page)
        self.assertIsNone(re.search(r'\son[a-z]+=', page))
        elements = Elements(page).elements
        self.assertEqual(sum(tag == 'script' for tag, _ in elements), 1)

    def test_noscript_copy(self):
        _, backlog = load_backlog(Config())
        page = render_board(backlog, repo="r")
        self.assertIn('All entries are shown in file order. Enable JavaScript to switch views and preview reordering.',
                     page)

    def test_custom_status_pill_class_is_s_custom(self):
        md = "| K417. Item | job | context | Blocked | Team |"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn('class="bw-pill bw-tone-h', page)
        self.assertIn('bw-pill--custom', page)

    def test_masthead_chips_waiting_and_only_code_markup(self):
        md = '# Title\n\nDescription `code`.\n\n'
        md += '| K417. Title | Job | **literal** [link](url) `code` | Ready<br>Waiting on: review<br>Sprint: S4 | Team |\n'
        page = render_board(parse_backlog(md), repo="tenant")
        for fragment in ('class="bw-masthead__eyebrow">tenant', '<h1>Title</h1>',
                         'Description <code>code</code>.', 'Source updated n/a',
                         'class="bw-chip bw-chip--sprint">S4',
                         'class="bw-pill bw-tone-waiting">Waiting</span> review',
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
        row = next(attrs for _, attrs in elements if 'data-stage' in attrs)
        self.assertEqual(row['data-stage'], payload)
        self.assertEqual(row['data-state'], 'open')

    def test_ordinary_item_has_no_pill(self):
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| K417. x | j | c |  | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertNotIn('class="bw-pill', page)

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
