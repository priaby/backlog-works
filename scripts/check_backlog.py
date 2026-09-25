#!/usr/bin/env python3
"""Format checker for docs/product/backlog.md.

Enforces the contract inherited from Crest's backlog_source.py (the write
path a future PBI-001 port must stay compatible with), plus the process
rules in AGENTS.md. Stdlib only. Exit 0 = clean, 1 = violations, 2 = usage.

Checks:
  - exactly one active table: the first contiguous run of lines starting
    with "| PBI-"; rows match ROW_ID_RE (id, optional sub-slice letter, period)
  - ids unique
  - every row has the same cell count as the header (5 columns)
  - Status cell (before the first <br>) is a legend value
  - at most one row is "In Progress"
  - a "## Bugs" section exists below the table
  - frontmatter "updated:" is an ISO date
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROW_ID_RE = re.compile(r"^\| (PBI-\d+[a-z]?)\. ")
STATUSES = {
    "Proposed",
    "Ready",
    "Planned",
    "In Progress",
    "Waiting",
    "Ready for Product Owner review",
    "Done",
    "Cancelled",
}
EXPECTED_COLUMNS = 5


def cell_count(row: str) -> int:
    return len(row.strip().strip("|").split("|"))


def row_status(row: str) -> str:
    cells = row.strip().strip("|").split("|")
    if len(cells) < 4:
        return ""
    return cells[3].split("<br>", 1)[0].strip()


def table_block(lines: list[str]) -> tuple[int, int]:
    start = next((i for i, l in enumerate(lines) if l.startswith("| PBI-")), -1)
    if start < 0:
        return -1, -1
    end = start
    while end < len(lines) and lines[end].startswith("| PBI-"):
        end += 1
    return start, end


def check(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    m = re.search(r"^updated:\s*(\S+)\s*$", text, re.M)
    if not m or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", m.group(1)):
        problems.append("frontmatter: missing or non-ISO `updated:` date")

    start, end = table_block(lines)
    if start < 0:
        problems.append("no `| PBI-` table found")
        return problems

    # header + separator must sit directly above the first row
    if start < 2 or not lines[start - 1].startswith("|---"):
        problems.append(f"line {start + 1}: table separator row `|---|...` missing above first PBI row")
    else:
        header_cells = cell_count(lines[start - 2])
        if header_cells != EXPECTED_COLUMNS:
            problems.append(f"line {start - 1}: header has {header_cells} cells, expected {EXPECTED_COLUMNS}")

    ids: list[str] = []
    in_progress = 0
    for i in range(start, end):
        row = lines[i]
        n = i + 1
        idm = ROW_ID_RE.match(row)
        if not idm:
            problems.append(f"line {n}: row does not match `| PBI-<digits>[a-z]. `")
            continue
        ids.append(idm.group(1))
        cc = cell_count(row)
        if cc != EXPECTED_COLUMNS:
            problems.append(f"line {n}: {idm.group(1)} has {cc} cells, expected {EXPECTED_COLUMNS}")
        st = row_status(row)
        if st not in STATUSES:
            problems.append(f"line {n}: {idm.group(1)} status {st!r} not in legend")
        if st == "In Progress":
            in_progress += 1

    for pbi, c in Counter(ids).items():
        if c > 1:
            problems.append(f"duplicate id {pbi} ({c} rows)")
    if in_progress > 1:
        problems.append(f"{in_progress} rows are `In Progress`; AGENTS.md allows one")

    later = lines[end:]
    if any(l.startswith("| PBI-") for l in later):
        problems.append("a second `| PBI-` block exists after the active table; only the first is machine-visible")
    if not any(l.strip() == "## Bugs" for l in later):
        problems.append("`## Bugs` section missing below the table")

    return problems


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("docs/product/backlog.md")
    if len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"check_backlog: {path} not found", file=sys.stderr)
        return 2
    problems = check(path)
    if problems:
        for p in problems:
            print(f"FAIL {path}: {p}")
        return 1
    start, end = table_block(path.read_text(encoding="utf-8").splitlines())
    print(f"ok {path}: {end - start} PBI rows, format valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
