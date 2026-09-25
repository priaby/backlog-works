# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Backlog domain: the markdown backlog file as data.

Owns parsing the `| PBI-` table, the status legend, and reorder/status-
change validation (same id set, same per-row cell count, only order or one
cell changes). Pure functions over text and small dataclasses. No I/O, no
network, no imports from other backlogworks modules.
"""
