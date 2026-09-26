# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Parity between docs/design-system.md and the shipped board CSS.

Enforces docs/design-system.md's own promise: "Parity is test-enforced
(every `--bw-*` token named here must exist in the CSS)", plus the rules
in its section 4 (no one-off colour literals outside the token block) and
the tone mapping in board.py._tone.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from backlogworks.backlog import parse_backlog
from backlogworks.config import Config
from backlogworks.local import load_backlog
from backlogworks.web.board import _tone, render_board
from backlogworks.web.board_assets import CSS

DOC = (Path(__file__).resolve().parents[2] / "docs" / "design-system.md").read_text()

_TOKEN_NAME_RE = re.compile(r"--bw-[a-z0-9-]+")
_CLASS_RE = re.compile(r"\bbw-[a-z0-9_-]+")
_COLOR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgb\(|rgba\(|hsl\(|hsla\(|oklch\(")
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


def _tokens_block_span(css: str) -> tuple[int, int]:
    start = css.index("/* tokens:start */")
    end = css.index("/* tokens:end */") + len("/* tokens:end */")
    return start, end


def _strip_comments(css: str) -> str:
    """Drop /* ... */ spans so a name mentioned only in a comment (e.g. the
    hex-fallback notes) does not read as a declaration."""
    return _CSS_COMMENT_RE.sub("", css)


class DesignTokenTests(unittest.TestCase):
    def test_every_doc_token_is_defined_in_css(self):
        # Doc table cells like `--bw-h1-*` truncate at the class boundary
        # (`*` is not a token-name character); a trailing "-" marks that
        # wildcard shorthand, not a real token name, so it is excluded.
        names = {n for n in _TOKEN_NAME_RE.findall(DOC) if not n.endswith("-")}
        self.assertTrue(names, "expected to find --bw-* tokens in the doc")
        declared = _strip_comments(CSS)
        missing = sorted(n for n in names if f"{n}:" not in declared)
        self.assertEqual(missing, [], f"tokens named in the doc but not defined in CSS: {missing}")

    def test_no_color_literals_outside_the_token_block(self):
        start, end = _tokens_block_span(CSS)
        outside = CSS[:start] + CSS[end:]
        hits = _COLOR_LITERAL_RE.findall(outside)
        self.assertEqual(hits, [], f"colour literal(s) outside tokens:start/tokens:end: {hits}")
        # Sanity: the token block itself does carry oklch() literals.
        self.assertIn("oklch(", CSS[start:end])

    def test_every_bw_class_in_the_rendered_board_has_a_css_selector(self):
        _, backlog = load_backlog(Config())
        page = render_board(backlog, repo="local/x")
        classes = set()
        for attrs in re.findall(r'class="([^"]+)"', page):
            classes.update(c for c in attrs.split() if c.startswith("bw-"))
        self.assertTrue(classes, "expected at least one bw-* class in the rendered board")
        missing = sorted(c for c in classes if not re.search(r"\." + re.escape(c) + r"(?![\w-])", CSS))
        self.assertEqual(missing, [], f"classes rendered but with no selector in CSS: {missing}")

    def test_tone_is_stable_and_fixed_statuses_map_as_specified(self):
        self.assertEqual(_tone("In Progress"), "progress")
        self.assertEqual(_tone("Ready"), "ready")
        self.assertEqual(_tone("Done"), "done")
        self.assertEqual(_tone(""), "neutral")
        first = _tone("Unknown")
        self.assertIn(first, {"h1", "h2", "h3", "h4"})
        self.assertEqual(_tone("Unknown"), first)  # stable within a process
        # ... and stable across a fresh parse/process boundary (crc32 seed
        # never changes, so re-deriving must reproduce the same hue).
        md = "| K417. x | j | c | Unknown | T |"
        page = render_board(parse_backlog(md), repo="r")
        self.assertIn(f"bw-tone-{first}", page)

    def test_reduced_motion_and_any_hover_present(self):
        self.assertIn("prefers-reduced-motion", CSS)
        self.assertIn("any-hover", CSS)


if __name__ == "__main__":
    unittest.main()
