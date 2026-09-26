# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Parse the backlog markdown into Items. Byte-preserving on the way back is
PBI-001's job; this module only reads."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ROW_ID_RE = re.compile(r"^\| (PBI-\d+[a-z]?)\. ")
ROW_PREFIX = "| PBI-"
EXPECTED_CELLS = 5
# Product Owner decision 2026-09-26: five statuses. A blocked item keeps its
# status and carries a "Waiting on: <condition>" note after <br>; cancelled
# rows are deleted from the file (git history keeps them).
STATUSES = (
    "Candidate",
    "Planned",
    "In Progress",
    "Review",
    "Done",
)
WAITING_PREFIX = "Waiting on:"


class FormatError(ValueError):
    """The file does not satisfy the backlog format contract."""


@dataclass(frozen=True)
class Item:
    id: str
    title: str
    core_job: str
    context: str
    status: str
    status_note: str  # free text after the first <br> in the Status cell
    driver: str
    line: int  # 1-based line in the source file

    @property
    def status_known(self) -> bool:
        return self.status in STATUSES

    @property
    def waiting_on(self) -> str:
        """The named external condition when the note starts with "Waiting on:"."""
        note = self.status_note
        return note[len(WAITING_PREFIX):].strip() if note.startswith(WAITING_PREFIX) else ""


@dataclass(frozen=True)
class Backlog:
    title: str
    updated: str
    items: tuple[Item, ...]
    table_start: int  # 0-based index of the first row line
    table_end: int  # 0-based index one past the last row line
    problems: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(i.id for i in self.items)

    @property
    def in_progress(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.status == "In Progress")


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def table_block(lines: list[str]) -> tuple[int, int]:
    start = next((i for i, l in enumerate(lines) if l.startswith(ROW_PREFIX)), -1)
    if start < 0:
        return -1, -1
    end = start
    while end < len(lines) and lines[end].startswith(ROW_PREFIX):
        end += 1
    return start, end


def _frontmatter(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def parse_backlog(markdown: str) -> Backlog:
    """Parse leniently, recording format problems instead of raising, so a
    board can still render a slightly broken file. Raises FormatError only
    when there is no table at all."""
    lines = markdown.splitlines()
    start, end = table_block(lines)
    if start < 0:
        raise FormatError("no `| PBI-` table found")
    fm = _frontmatter(lines)
    problems: list[str] = []
    items: list[Item] = []
    seen: set[str] = set()
    for i in range(start, end):
        row = lines[i]
        m = ROW_ID_RE.match(row)
        if not m:
            problems.append(f"line {i + 1}: row does not start with `| PBI-<n>. `")
            continue
        cells = _cells(row)
        if len(cells) != EXPECTED_CELLS:
            problems.append(f"line {i + 1}: {m.group(1)} has {len(cells)} cells, expected {EXPECTED_CELLS}")
            cells = (cells + [""] * EXPECTED_CELLS)[:EXPECTED_CELLS]
        pbi_id = m.group(1)
        if pbi_id in seen:
            problems.append(f"line {i + 1}: duplicate id {pbi_id}")
        seen.add(pbi_id)
        title = cells[0][len(pbi_id) + 1 :].strip()
        status_cell = cells[3]
        status, _, note = status_cell.partition("<br>")
        item = Item(pbi_id, title, cells[1], cells[2], status.strip(), note.strip(), cells[4], i + 1)
        if not item.status_known:
            problems.append(f"line {i + 1}: {pbi_id} status {item.status!r} not in legend")
        items.append(item)
    if any(l.startswith(ROW_PREFIX) for l in lines[end:]):
        problems.append("a second `| PBI-` block exists after the active table")
    if len([i for i in items if i.status == "In Progress"]) > 1:
        problems.append("more than one row is `In Progress`")
    title = fm.get("title") or next((l[2:].strip() for l in lines if l.startswith("# ")), "Product Backlog")
    return Backlog(title, fm.get("updated", ""), tuple(items), start, end, tuple(problems))
