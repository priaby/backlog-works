#!/usr/bin/env python3
"""Print a fresh item id for argv[1] (default docs/product/backlog.md)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from backlogworks.backlog import FormatError, new_item_id, parse_backlog  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1]) if len(argv) > 1 else Path("docs/product/backlog.md")
    try:
        backlog = parse_backlog(path.read_text(encoding="utf-8"))
        if backlog.problems:
            raise FormatError("; ".join(backlog.problems))
        print(new_item_id(backlog.ids))
    except (OSError, FormatError) as exc:
        print(f"new_id: {path}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
