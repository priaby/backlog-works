# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import check_backlog

MINIMAL = """---
title: "T"
updated: 2026-09-25
---
# T

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| K417. First | job | ctx | In Progress | Team |
| A100. Second | job | ctx | Done | PO |
"""


class CheckBacklogTests(unittest.TestCase):
    def test_unknown_status_fails_with_line_and_id(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "backlog.md"
            path.write_text(MINIMAL.replace("| Done | PO |", "| Shipped | PO |"), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = check_backlog.main(["x", str(path)])
            self.assertEqual(code, 1)
            self.assertIn(f"FAIL {path}: line 10: A100 status 'Shipped' not in legend", out.getvalue())

    def test_clean_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "backlog.md"
            path.write_text(MINIMAL, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = check_backlog.main(["x", str(path)])
            self.assertEqual(code, 0)
            self.assertEqual(out.getvalue().strip(), f"ok {path}: 2 item rows, format valid")


if __name__ == "__main__":
    unittest.main()
