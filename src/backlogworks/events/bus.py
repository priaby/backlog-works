# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""In-process event bus. Stdlib only, thread-safe, synchronous dispatch."""

from __future__ import annotations

import datetime as dt
import json
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Handler = Callable[["Event"], None]


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Event:
    """Something that happened. Past tense name, immutable, JSON-able payload.

    `name` is the catalogue key from docs/architecture.md (e.g.
    "backlog.loaded"); `actor` is "system", "po:<session>" or "agent:<key>";
    `repo` is the tenant (customer repo) or "" for service-level events.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    actor: str = "system"
    repo: str = ""
    occurred_at: str = field(default_factory=_utc_now)

    def to_json(self) -> str:
        return json.dumps(
            {"event": self.name, "at": self.occurred_at, "actor": self.actor, "repo": self.repo, **self.payload},
            separators=(",", ":"),
            sort_keys=True,
        )


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}
        self._any: list[Handler] = []
        self._lock = threading.Lock()

    def subscribe(self, name: str | None, handler: Handler) -> None:
        """Subscribe to one event name, or to every event with name=None."""
        with self._lock:
            if name is None:
                self._any.append(handler)
            else:
                self._handlers.setdefault(name, []).append(handler)

    def publish(self, event: Event) -> None:
        with self._lock:
            handlers = list(self._handlers.get(event.name, ())) + list(self._any)
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001 - subscriber isolation is the contract
                print(
                    json.dumps({"event": "events.handler_failed", "for": event.name,
                                "handler": getattr(handler, "__name__", repr(handler)), "error": repr(exc)}),
                    file=sys.stderr, flush=True,
                )


def audit_to_stderr(event: Event) -> None:
    """Default subscriber: one structured JSON line per event (Railway captures stderr)."""
    print(event.to_json(), file=sys.stderr, flush=True)
