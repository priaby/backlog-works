# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import hashlib
import tempfile
import unittest
from pathlib import Path

from backlogworks.config import Config
from backlogworks.events import Event, EventBus
from backlogworks.local import LOCAL_REPO, load_backlog


class LoadBacklogTests(unittest.TestCase):
    def test_loads_exact_text_of_configured_file(self):
        config = Config()
        expected = Path(config.backlog_file).read_text(encoding="utf-8")
        markdown, backlog = load_backlog(config)
        self.assertEqual(markdown, expected)
        self.assertGreater(len(backlog.items), 0)

    def test_event_payload_hashes_exact_bytes(self):
        content = b"# Example\r\n| K417. Example | Job | Context | Ready | Team |\r\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir) / "backlog.md"
            tmp.write_bytes(content)
            config = Config(backlog_file=tmp)
            bus = EventBus()
            seen: list[Event] = []
            bus.subscribe("backlog.loaded", seen.append)
            markdown, backlog = load_backlog(config, bus)
        self.assertEqual(markdown.encode("utf-8"), content)
        self.assertEqual(seen[0].payload, {
            "source": "local", "sha": hashlib.sha1(content).hexdigest(),
            "items": len(backlog.items), "problems": len(backlog.problems),
        })
        self.assertEqual(seen[0].repo, LOCAL_REPO)


if __name__ == "__main__":
    unittest.main()
