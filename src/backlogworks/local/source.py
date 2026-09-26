# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
from __future__ import annotations

import hashlib
from pathlib import Path

from backlogworks.backlog import Backlog, parse_backlog
from backlogworks.config import Config
from backlogworks.events import Event, EventBus

LOCAL_REPO = "priaby/backlog-works"


def load_backlog(config: Config, bus: EventBus | None = None) -> tuple[str, Backlog]:
    content = Path(config.backlog_file).read_bytes()
    markdown = content.decode("utf-8")
    backlog = parse_backlog(markdown)
    if bus is not None:
        bus.publish(Event("backlog.loaded", {"source": "local", "sha": hashlib.sha1(content).hexdigest(),
                                             "items": len(backlog.items),
                                             "problems": len(backlog.problems)}, repo=LOCAL_REPO))
    return markdown, backlog
