# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import unittest
from pathlib import Path

from backlogworks.backlog import Bug, FormatError, parse_backlog, parse_bugs

DEMO = Path(__file__).resolve().parents[2] / "src/backlogworks/demo/backlog.md"
REPO_BACKLOG = Path(__file__).resolve().parents[2] / "docs/product/backlog.md"

MINIMAL = """---
title: "T"
updated: 2026-09-25
---
# T

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| PBI-001. First | job | ctx `code` | In Progress<br>Sprint: S1 | Team |
| PBI-002a. Sub slice | job | ctx | Done | PO |

## Bugs
"""


class ParseTests(unittest.TestCase):
    def test_description_is_first_paragraph_after_h1(self):
        md = MINIMAL.replace("# T\n", "# T\n\nFirst `line` with <html>.\nSecond line.\n\nIgnored.\n")
        self.assertEqual(parse_backlog(md).description, "First `line` with <html>. Second line.")

    def test_description_missing_does_not_swallow_blocks(self):
        for md in (MINIMAL, MINIMAL.replace("# T", ""),
                   MINIMAL.replace("# T", "# T\n\n## Section\nNot description.")):
            self.assertEqual(parse_backlog(md).description, "")

    def test_bugs_and_continuations_are_scoped_to_section(self):
        md = MINIMAL + """
- **BUG-one** First `issue` <html>.
  Continued on another line.

  Another paragraph.
- Unrelated bullet.
  Must not attach to the previous bug.
- **BUG-two** Second issue.
## Later
- **BUG-outside** Not a bug in this section.
"""
        self.assertEqual(parse_backlog(md).bugs, (
            Bug("BUG-one", "First `issue` <html>. Continued on another line. Another paragraph."),
            Bug("BUG-two", "Second issue."),
        ))

    def test_empty_missing_and_fenced_bug_examples(self):
        for md in ("", "## Bugs\n(none yet)", "- **BUG-outside** Ignored"):
            self.assertEqual(parse_bugs(md), ())
        md = "## Bugs\n```markdown\n- **BUG-example** Ignore\n```\n- **BUG-real** Keep"
        self.assertEqual(parse_bugs(md), (Bug("BUG-real", "Keep"),))

    def test_minimal(self):
        b = parse_backlog(MINIMAL)
        self.assertEqual(b.title, "T")
        self.assertEqual(b.updated, "2026-09-25")
        self.assertEqual(b.ids, ("PBI-001", "PBI-002a"))
        self.assertEqual(b.items[0].title, "First")
        self.assertEqual(b.items[0].status, "In Progress")
        self.assertEqual(b.items[0].status_note, "Sprint: S1")
        self.assertEqual(b.items[1].status_note, "")
        self.assertEqual(b.problems, ())

    def test_no_table_raises(self):
        with self.assertRaises(FormatError):
            parse_backlog("# nothing here\n")

    def test_problems_are_recorded_not_raised(self):
        broken = MINIMAL.replace("| Done | PO |", "| Shipped | PO |").replace("PBI-002a.", "PBI-001.")
        b = parse_backlog(broken)
        self.assertEqual(len(b.items), 2)
        self.assertTrue(any("duplicate id PBI-001" in p for p in b.problems))
        self.assertTrue(any("not in legend" in p for p in b.problems))

    def test_waiting_note(self):
        md = MINIMAL.replace("In Progress<br>Sprint: S1", "Ready<br>Waiting on: legal sign-off")
        b = parse_backlog(md)
        self.assertEqual(b.items[0].status, "Ready")
        self.assertEqual(b.items[0].waiting_on, "legal sign-off")
        self.assertEqual(b.items[1].waiting_on, "")
        self.assertEqual(b.problems, ())

    def test_empty_status_is_ordinary_and_several_in_progress_allowed(self):
        md = MINIMAL.replace("In Progress<br>Sprint: S1", "").replace("| Done |", "| In Progress |")
        b = parse_backlog(md)
        self.assertEqual(b.items[0].status, "")
        self.assertTrue(b.items[0].status_known)
        self.assertEqual(b.problems, ())
        two = MINIMAL.replace("| Done |", "| In Progress |")
        self.assertEqual(parse_backlog(two).problems, ())

    def test_demo_and_repo_files_are_clean(self):
        for path in (DEMO, REPO_BACKLOG):
            b = parse_backlog(path.read_text(encoding="utf-8"))
            self.assertEqual(b.problems, (), path)
            self.assertGreater(len(b.items), 0, path)


if __name__ == "__main__":
    unittest.main()
