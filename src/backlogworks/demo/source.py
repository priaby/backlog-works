# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
from __future__ import annotations

from pathlib import Path

from backlogworks.backlog import Backlog, parse_backlog
from backlogworks.events import Event, EventBus

DEMO_REPO = "demo/lighthouse"
_FILE = Path(__file__).with_name("backlog.md")


def load_demo(bus: EventBus | None = None) -> tuple[str, Backlog]:
    markdown = _FILE.read_text(encoding="utf-8")
    backlog = parse_backlog(markdown)
    if bus is not None:
        bus.publish(Event("backlog.loaded", {"source": "packaged", "items": len(backlog.items),
                                             "problems": len(backlog.problems)}, repo=DEMO_REPO))
    return markdown, backlog
