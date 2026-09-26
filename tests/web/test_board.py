# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import hashlib
import unittest
from unittest.mock import patch

from backlogworks.backlog import parse_backlog
from backlogworks.demo import load_demo
from backlogworks.demo import source
from backlogworks.events import Event, EventBus
from backlogworks.web.board import render_board


class BoardTests(unittest.TestCase):
    def test_demo_renders_every_item_in_order_and_escapes(self):
        seen: list[Event] = []
        bus = EventBus()
        bus.subscribe("backlog.loaded", seen.append)
        _, backlog = load_demo(bus)
        page = render_board(backlog, repo="demo/x")
        positions = [page.index(f'id="{i}"') for i in backlog.ids]
        self.assertEqual(positions, sorted(positions))
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
        md = "| a | b | c | d | e |\n|---|---|---|---|---|\n| PBI-001. <b>x</b> | j | c | Planned | T |\n"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)
        self.assertNotIn("<b>x</b>", page)

    def test_bus_isolates_failing_handler(self):
        bus = EventBus()
        calls = []
        bus.subscribe("x", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        bus.subscribe("x", calls.append)
        bus.publish(Event("x"))
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
