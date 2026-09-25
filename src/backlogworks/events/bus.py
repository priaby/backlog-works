# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""In-process event bus. Stdlib only, thread-safe, synchronous dispatch."""

from __future__ import annotations

import datetime as dt
import json
import sys
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Handler = Callable[["Event"], None]


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_json(value: Any) -> None:
    """Reject Python extensions to JSON, including tuples and non-string keys."""
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise TypeError("JSON object keys must be strings")
            _validate_json(child)
    elif type(value) is list:
        for child in value:
            _validate_json(child)
    elif type(value) not in (str, int, float, bool, type(None)):
        raise TypeError("Unsupported JSON value type")


@dataclass(frozen=True, init=False)
class Event:
    """An immutable fact with a JSON snapshot and independent payload copies.

    `name` is the catalogue key from docs/architecture.md (e.g.
    "backlog.loaded"); `actor` is "system", "po:<session>" or "agent:<key>";
    `repo` is the tenant (customer repo) or "" for service-level events.
    Mutating a returned payload never changes the event or another subscriber's
    view. Construction rejects unsupported types, cycles and non-finite numbers.
    """

    name: str
    _payload_json: str = field(repr=False)
    actor: str
    repo: str
    occurred_at: str
    event_id: str
    schema_version: int

    def __init__(self, name: str, payload: dict[str, Any] | None = None,
                 actor: str = "system", repo: str = "", occurred_at: str | None = None) -> None:
        data = {} if payload is None else payload
        if type(data) is not dict:
            raise TypeError("Event payload must be a JSON object")
        # Encode first to reject cycles and non-finite numbers before walking.
        snapshot = json.dumps(data, allow_nan=False, separators=(",", ":"))
        _validate_json(data)
        for key, value in {
            "name": name, "_payload_json": snapshot, "actor": actor, "repo": repo,
            "occurred_at": _utc_now() if occurred_at is None else occurred_at,
            "event_id": uuid.uuid4().hex, "schema_version": 1,
        }.items():
            object.__setattr__(self, key, value)

    @property
    def payload(self) -> dict[str, Any]:
        return json.loads(self._payload_json)

    def to_json(self) -> str:
        return json.dumps(
            {"event": self.name, "at": self.occurred_at, "actor": self.actor,
             "repo": self.repo, "event_id": self.event_id,
             "schema_version": self.schema_version, "payload": self.payload},
            allow_nan=False, separators=(",", ":"), sort_keys=True,
        )


class EventBus:
    """Synchronous observers in registration order across all subscriptions.

    Reentrant publishes complete before control returns to the publishing
    handler. Concurrent publishes may interleave; no global order is promised.
    Subscriptions added during a publish apply only to later publishes.
    """

    def __init__(self) -> None:
        self._handlers: list[tuple[str | None, Handler]] = []
        self._lock = threading.Lock()

    def subscribe(self, name: str | None, handler: Handler) -> None:
        """Subscribe to one event name, or to every event with name=None."""
        with self._lock:
            self._handlers.append((name, handler))

    def publish(self, event: Event) -> None:
        with self._lock:
            handlers = [handler for name, handler in self._handlers
                        if name is None or name == event.name]
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001 - subscriber isolation is the contract
                try:
                    owner = handler if hasattr(handler, "__qualname__") else type(handler)
                    module = (getattr(owner, "__module__", None)
                              or type(getattr(handler, "__self__", handler)).__module__)
                    identifier = f"{module}.{owner.__qualname__}"
                    print(json.dumps({"event": "events.handler_failed", "for": event.name,
                                      "handler": identifier, "error": type(exc).__name__}),
                          file=sys.stderr, flush=True)
                except Exception:
                    # Optional diagnostics must never interrupt remaining observers.
                    pass


def audit_to_stderr(event: Event) -> None:
    """Default subscriber: one structured JSON line per event (Railway captures stderr)."""
    print(event.to_json(), file=sys.stderr, flush=True)
