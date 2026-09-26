# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Backlog domain: the markdown backlog file as data. Pure, no I/O.

Owns the file format contract (docs/architecture.md section 5): the first
contiguous `| PBI-` table is the active backlog, rows are items, the
status legend is the vocabulary. Reorder and status-change validation
(same id set, same per-row cell count, nothing else changes) arrive with
PBI-001. No imports from other backlogworks modules.
"""

from backlogworks.backlog.model import (
    STATUSES, WAITING_PREFIX, Backlog, Bug, FormatError, Item, parse_backlog, parse_bugs,
)

__all__ = ["STATUSES", "WAITING_PREFIX", "Backlog", "Bug", "FormatError", "Item",
           "parse_backlog", "parse_bugs"]
