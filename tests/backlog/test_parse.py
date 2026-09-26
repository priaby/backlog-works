# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
import re
import unittest
from pathlib import Path
from unittest.mock import Mock

from backlogworks.backlog import FormatError, new_item_id, parse_backlog

DEMO = Path(__file__).resolve().parents[2] / "src/backlogworks/demo/backlog.md"
REPO_BACKLOG = Path(__file__).resolve().parents[2] / "docs/product/backlog.md"

MINIMAL = """---
title: "T"
updated: 2026-09-25
---
# T

| Item (PBI) | Core Job | Context | Status | Driver |
|---|---|---|---|---|
| K417. First | job | ctx `code` | In Progress<br>Sprint: S1 | Team |
| A100. Second | job | ctx | Done | PO |
"""


class ParseTests(unittest.TestCase):
    def test_description_is_first_paragraph_after_h1(self):
        md = MINIMAL.replace("# T\n", "# T\n\nFirst `line` with <html>.\nSecond line.\n\nIgnored.\n")
        self.assertEqual(parse_backlog(md).description, "First `line` with <html>. Second line.")

    def test_description_missing_does_not_swallow_blocks(self):
        for md in (MINIMAL, MINIMAL.replace("# T", ""),
                   MINIMAL.replace("# T", "# T\n\n## Section\nNot description.")):
            self.assertEqual(parse_backlog(md).description, "")

    def test_minimal(self):
        b = parse_backlog(MINIMAL)
        self.assertEqual(b.title, "T")
        self.assertEqual(b.updated, "2026-09-25")
        self.assertEqual(b.ids, ("K417", "A100"))
        self.assertEqual(b.items[0].title, "First")
        self.assertEqual(b.items[0].status, "In Progress")
        self.assertEqual(b.items[0].status_note, "Sprint: S1")
        self.assertEqual(b.items[1].status_note, "")
        self.assertEqual(b.problems, ())

    def test_no_table_raises(self):
        with self.assertRaisesRegex(FormatError, "^no item table found$"):
            parse_backlog("# nothing here\n")

    def test_problems_are_recorded_not_raised(self):
        broken = MINIMAL.replace("| Done | PO |", "| Shipped | PO |").replace("A100.", "K417.")
        b = parse_backlog(broken)
        self.assertEqual(len(b.items), 2)
        self.assertTrue(any("duplicate id K417" in p for p in b.problems))
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

    def test_demo_file_is_clean(self):
        b = parse_backlog(DEMO.read_text(encoding="utf-8"))
        self.assertEqual(b.problems, ())
        self.assertEqual(len(b.items), 12)
        self.assertTrue(all(re.fullmatch(r"[ABCDEFGHJKLMNPRSTUVWXYZ][1-9][0-9]{2}", i)
                            for i in b.ids))

    def test_repo_file_is_clean(self):
        b = parse_backlog(REPO_BACKLOG.read_text(encoding="utf-8"))
        self.assertEqual(b.problems, ())
        self.assertGreater(len(b.items), 0)
        for item_id in b.ids:
            self.assertRegex(item_id, r"^[ABCDEFGHJKLMNPRSTUVWXYZ][1-9][0-9]{2}$")

    def test_invalid_ids_have_line_problems(self):
        for invalid in ("PBI-001", "K41", "K4170", "I417", "O417", "Q417", "K099", "k417", "K417a", "K٤١٧"):
            with self.subTest(invalid=invalid):
                markdown = MINIMAL.replace("A100", invalid)
                b = parse_backlog(markdown)
                line = next(i for i, text in enumerate(markdown.splitlines(), 1)
                            if text.startswith("| " + invalid + ". "))
                self.assertEqual(b.ids, ("K417",))
                self.assertIn(f"line {line}: row does not start with `| <Letter><3 digits>. `", b.problems)

    def test_missing_period_has_line_problem(self):
        b = parse_backlog(MINIMAL.replace("A100.", "A100"))
        self.assertEqual(b.ids, ("K417",))
        self.assertIn("line 10: row does not start with `| <Letter><3 digits>. `", b.problems)

    def test_table_location_is_first_contiguous_regex_run(self):
        from backlogworks.backlog.model import table_block
        rows = ["| PBI-001. Legacy | x | x | Ready | x |", "# Header",
                "| K417. First | x | x | Ready | x |", "| A100. Second | x | x | Done | x |",
                "", "| Z999. Later | x | x | Ready | x |"]
        self.assertEqual(table_block(rows), (2, 4))
        b = parse_backlog("\n".join(rows))
        self.assertEqual((b.table_start, b.table_end), (2, 4))
        self.assertEqual(b.ids, ("K417", "A100"))
        self.assertIn("a second item block exists after the active table", b.problems)

    def test_malformed_row_before_active_run_is_reported(self):
        b = parse_backlog(MINIMAL.replace("K417.", "K417"))
        self.assertEqual(b.ids, ("A100",))
        self.assertIn("line 9: row does not start with `| <Letter><3 digits>. `", b.problems)

    def test_malformed_row_ends_active_run(self):
        md = MINIMAL.replace("| A100.", "| K41. Bad | j | c | Ready | Team |\n| A100.")
        b = parse_backlog(md)
        self.assertEqual(b.ids, ("K417",))
        self.assertEqual(len(b.problems), 2)


class NewIdTests(unittest.TestCase):
    def test_injected_rng_and_number_boundaries(self):
        rng = Mock()
        rng.choice.return_value = "K"
        rng.randbelow.side_effect = [0, 899]
        self.assertEqual(new_item_id((), rng=rng), "K100")
        self.assertEqual(new_item_id((), rng=rng), "K999")
        rng.choice.assert_called_with("ABCDEFGHJKLMNPRSTUVWXYZ")
        rng.randbelow.assert_called_with(900)

    def test_retries_existing_without_mutating_collection(self):
        existing = {"K417"}
        rng = Mock()
        rng.choice.return_value = "K"
        rng.randbelow.side_effect = [317, 318]
        self.assertEqual(new_item_id(existing, rng=rng), "K418")
        self.assertEqual(existing, {"K417"})

    def test_exhaustion_is_bounded_to_1000_attempts(self):
        rng = Mock()
        rng.choice.return_value = "K"
        rng.randbelow.return_value = 317
        with self.assertRaisesRegex(FormatError, "1000 tries"):
            new_item_id(["K417"], rng=rng)
        self.assertEqual(rng.choice.call_count, 1000)
        self.assertEqual(rng.randbelow.call_count, 1000)

    def test_default_rng_returns_valid_fresh_id(self):
        self.assertRegex(new_item_id({"K417"}), r"^[ABCDEFGHJKLMNPRSTUVWXYZ][1-9][0-9]{2}$")


if __name__ == "__main__":
    unittest.main()
