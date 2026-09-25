# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Composition root: `python -m backlogworks`. Builds the bus, subscribes
consumers, starts the HTTP server. Wiring only, no logic."""

from backlogworks.config import Config
from backlogworks.events import EventBus, audit_to_stderr
from backlogworks.web.server import serve


def build_bus() -> EventBus:
    bus = EventBus()
    bus.subscribe(None, audit_to_stderr)
    return bus


def main() -> None:
    serve(Config.from_env(), build_bus())


if __name__ == "__main__":
    main()
