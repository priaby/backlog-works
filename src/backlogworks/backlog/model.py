# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Parse the backlog markdown into Items. Byte-preserving on the way back is
PBI-001's job; this module only reads."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ROW_ID_RE = re.compile(r"^\| (PBI-\d+[a-z]?)\. ")
ROW_PREFIX = "| PBI-"
EXPECTED_CELLS = 5
# Product Owner decision 2026-09-26, grounded in the Scrum Guide 2020 and
# the ScrumPLoP "Definition of Ready" pattern: an ordinary item has no
# status (empty cell); "Ready" = meets the Definition of Ready after
# refinement and may be selected in Sprint Planning ("ready for selection",
# Scrum Guide, Product Backlog); "In Progress" = selected into a Sprint
# (Sprint Backlog); "Done" = meets the Definition of Done. Anything else is a
# note after <br> (e.g. "Sprint: S4", "Waiting on: <condition>"). Cancelled
# rows are deleted from the file; git history keeps them.
STATUSES = (
    "",
    "Ready",
    "In Progress",
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
class Bug:
    id: str
    text: str


@dataclass(frozen=True)
class Backlog:
    title: str
    updated: str
    items: tuple[Item, ...]
    table_start: int  # 0-based index of the first row line
    table_end: int  # 0-based index one past the last row line
    problems: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    bugs: tuple[Bug, ...] = field(default_factory=tuple)

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


def _description(lines: list[str]) -> str:
    """Join the first prose paragraph after the H1 into one display line."""
    heading = next((i for i, line in enumerate(lines) if line.startswith("# ")), -1)
    if heading < 0:
        return ""
    paragraph: list[str] = []
    for line in lines[heading + 1:]:
        text = line.strip()
        if not text:
            if paragraph:
                break
            continue
        if re.match(r"^(?:[#>|]|[-*+]\s|\d+\.\s|```|~~~)", text):
            break
        paragraph.append(text)
    return " ".join(paragraph)


def parse_bugs(markdown: str) -> tuple[Bug, ...]:
    """Read bug bullets and indented continuations only within ## Bugs."""
    bugs: list[Bug] = []
    active = False
    current_id = ""
    parts: list[str] = []
    fence = ""

    def finish() -> None:
        if current_id:
            bugs.append(Bug(current_id, " ".join(parts)))

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            if not fence:
                fence = stripped[:3]
            elif stripped.startswith(fence):
                fence = ""
            continue
        if fence:
            continue
        if re.match(r"^#{1,2}\s", line):
            if active:
                break
            active = stripped == "## Bugs"
            continue
        if not active:
            continue
        match = re.match(r"^- \*\*(BUG-[^*\s]+)\*\*\s*(.*)$", line)
        if match:
            finish()
            current_id, first = match.groups()
            parts = [first] if first else []
        elif current_id and line.startswith(("  ", "\t")) and stripped:
            parts.append(stripped)
        elif stripped:
            finish()
            current_id, parts = "", []
    finish()
    return tuple(bugs)


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
    title = fm.get("title") or next((l[2:].strip() for l in lines if l.startswith("# ")), "Product Backlog")
    return Backlog(title, fm.get("updated", ""), tuple(items), start, end,
                   tuple(problems), _description(lines), parse_bugs(markdown))
