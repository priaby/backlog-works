# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Parse the backlog markdown into Items. Byte-preserving on the way back is
J709's job; this module only reads."""

from __future__ import annotations

import re
import secrets
from collections.abc import Collection
from dataclasses import dataclass, field

ROW_ID_RE = re.compile(r"^\| ([A-Z]\d{3})\. ")
ID_ALPHABET = "ABCDEFGHJKLMNPRSTUVWXYZ"
ITEM_ID_RE = re.compile(rf"[{ID_ALPHABET}][1-9][0-9]{{2}}")
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
# View order for the board's status selector (PO decision 2026-09-26): known
# statuses first, then any custom status in first-seen document order.
KNOWN_STATUSES = ("In Progress", "Ready", "Done")
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
    def state(self) -> str:
        """Two-tier state: "done" on an exact "Done" status, else "open"."""
        return "done" if self.status == "Done" else "open"

    @property
    def stage(self) -> str:
        """The open item's optional status; empty once the item is done."""
        return "" if self.state == "done" else self.status

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
    description: str = ""

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(i.id for i in self.items)

    @property
    def in_progress(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.status == "In Progress")

    @property
    def open_items(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.state == "open")

    @property
    def statuses(self) -> tuple[str, ...]:
        """Kept for scripts/check_backlog.py's own status legend check and
        for R685 (Configurable statuses per backlog); the board's fixed
        Open/In progress/Done/All view control no longer reads this.

        KNOWN_STATUSES always present, then each non-empty custom status
        (exact string match, so `done` counts as custom) in document order."""
        out = list(KNOWN_STATUSES)
        for item in self.items:
            if item.status and item.status not in out:
                out.append(item.status)
        return tuple(out)


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def table_block(lines: list[str]) -> tuple[int, int]:
    start = next((i for i, l in enumerate(lines) if ROW_ID_RE.match(l)), -1)
    if start < 0:
        return -1, -1
    end = start
    while end < len(lines) and ROW_ID_RE.match(lines[end]):
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


def new_item_id(existing: Collection[str], *, rng=secrets) -> str:
    """Choose an unused id; rng supplies choice(sequence) and randbelow(limit)."""
    for _ in range(1000):
        item_id = rng.choice(ID_ALPHABET) + str(100 + rng.randbelow(900))
        if item_id not in existing:
            return item_id
    raise FormatError("could not generate an unused item id after 1000 tries")


def _row_problem(line: int) -> str:
    return f"line {line}: row does not start with `| <Letter><3 digits>. `"


def parse_backlog(markdown: str) -> Backlog:
    """Parse leniently, recording format problems instead of raising, so a
    board can still render a slightly broken file. Raises FormatError only
    when there is no table at all."""
    lines = markdown.splitlines()
    start, end = table_block(lines)
    if start < 0:
        raise FormatError("no item table found")
    fm = _frontmatter(lines)
    problems: list[str] = []
    # Locate strictly by regex, but diagnose malformed adjacent table rows too.
    # They must not silently disappear when they break the active run.
    table_top, table_bottom = start, end
    while table_top > 0 and lines[table_top - 1].startswith("|"):
        table_top -= 1
    while table_bottom < len(lines) and lines[table_bottom].startswith("|"):
        table_bottom += 1
    for i in range(table_top, table_bottom):
        row = lines[i]
        if ROW_ID_RE.match(row):
            continue
        if all(re.fullmatch(r":?-+:?", cell) for cell in _cells(row)):
            continue
        if i + 1 < len(lines) and all(re.fullmatch(r":?-+:?", c) for c in _cells(lines[i + 1])):
            continue  # the header row: any cell text directly above the separator
        problems.append(_row_problem(i + 1))
    items: list[Item] = []
    seen: set[str] = set()
    for i in range(start, end):
        row = lines[i]
        m = ROW_ID_RE.match(row)
        if not m or not ITEM_ID_RE.fullmatch(m.group(1)):
            problems.append(_row_problem(i + 1))
            continue
        cells = _cells(row)
        if len(cells) != EXPECTED_CELLS:
            problems.append(f"line {i + 1}: {m.group(1)} has {len(cells)} cells, expected {EXPECTED_CELLS}")
            cells = (cells + [""] * EXPECTED_CELLS)[:EXPECTED_CELLS]
        item_id = m.group(1)
        if item_id in seen:
            problems.append(f"line {i + 1}: duplicate id {item_id}")
        seen.add(item_id)
        title = cells[0][len(item_id) + 1 :].strip()
        status_cell = cells[3]
        status, _, note = status_cell.partition("<br>")
        item = Item(item_id, title, cells[1], cells[2], status.strip(), note.strip(), cells[4], i + 1)
        items.append(item)
    if any(ROW_ID_RE.match(l) for l in lines[end:]):
        problems.append("a second item block exists after the active table")
    title = fm.get("title") or next((l[2:].strip() for l in lines if l.startswith("# ")), "Product Backlog")
    return Backlog(title, fm.get("updated", ""), tuple(items), start, end,
                   tuple(problems), _description(lines))
