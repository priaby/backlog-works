# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import unittest
from pathlib import Path

from backlogworks.config import APP_ROOT, Config


class BacklogFileTests(unittest.TestCase):
    def test_default_is_repo_backlog_and_exists(self):
        config = Config()
        self.assertEqual(config.backlog_file, APP_ROOT / "docs/product/backlog.md")
        self.assertTrue(Path(config.backlog_file).is_file())

    def test_from_env_empty_gives_default(self):
        config = Config.from_env({})
        self.assertEqual(config.backlog_file, APP_ROOT / "docs/product/backlog.md")

    def test_from_env_relative_path_is_rooted_at_app_root(self):
        config = Config.from_env({"BACKLOG_FILE": "x/y.md"})
        self.assertEqual(config.backlog_file, APP_ROOT / "x/y.md")

    def test_from_env_absolute_path_is_kept_as_is(self):
        config = Config.from_env({"BACKLOG_FILE": "/tmp/somewhere/backlog.md"})
        self.assertEqual(config.backlog_file, Path("/tmp/somewhere/backlog.md"))


if __name__ == "__main__":
    unittest.main()
