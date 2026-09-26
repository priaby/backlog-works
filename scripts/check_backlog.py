#!/usr/bin/env python3
"""Format checker for a backlog markdown file (default docs/product/backlog.md).

Thin wrapper over backlogworks.backlog.parse_backlog so the repo's own
backlog is validated by the same code the product ships. Adds a
repo-process check: the frontmatter `updated:` must be an ISO date.
Exit 0 clean, 1 violations, 2 usage.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backlogworks.backlog import FormatError, parse_backlog  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1]) if len(argv) > 1 else Path("docs/product/backlog.md")
    if not path.is_file():
        print(f"check_backlog: {path} not found", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    try:
        backlog = parse_backlog(text)
    except FormatError as exc:
        print(f"FAIL {path}: {exc}")
        return 1
    problems = list(backlog.problems)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", backlog.updated):
        problems.append("frontmatter: missing or non-ISO `updated:` date")
    for p in problems:
        print(f"FAIL {path}: {p}")
    if problems:
        return 1
    print(f"ok {path}: {len(backlog.items)} item rows, format valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
