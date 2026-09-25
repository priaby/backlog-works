# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Composition root: `python -m backlogworks`. Builds the bus, subscribes
consumers, starts the HTTP server. Wiring only, no logic."""

from backlogworks.config import Config
from backlogworks.events import Event, EventBus, audit_to_stderr
from backlogworks.web.server import build_server


def build_bus() -> EventBus:
    bus = EventBus()
    bus.subscribe(None, audit_to_stderr)
    return bus


def main() -> None:
    config = Config.from_env()
    bus = build_bus()
    with build_server(config, bus) as server:
        bus.publish(Event("service.started", {"port": server.server_port}))
        server.serve_forever()


if __name__ == "__main__":
    main()
