# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Regression tests for immutable facts and isolated synchronous observers."""

import io
import json
import unittest
import uuid
from dataclasses import FrozenInstanceError, is_dataclass
from unittest.mock import patch

from backlogworks.events import Event, EventBus, audit_to_stderr


class EventTests(unittest.TestCase):
    def test_payload_snapshot_and_subscriber_copies(self):
        original = {"nested": [{"value": 1}], "types": [True, None, 2.5, "text"]}
        event = Event("changed", original)
        original["nested"][0]["value"] = 2
        first = event.payload
        first["nested"][0]["value"] = 3
        bus = EventBus()
        bus.subscribe(None, lambda e: e.payload["nested"][0].update(value=4))
        observed = []
        bus.subscribe(None, lambda e: observed.append(e.payload))
        bus.publish(event)
        self.assertEqual(observed[0]["nested"][0]["value"], 1)
        self.assertEqual(json.loads(event.to_json())["payload"], event.payload)
        self.assertEqual(event.payload["types"], [True, None, 2.5, "text"])

    def test_envelope_is_authoritative_and_dataclass_frozen(self):
        forged = dict(event="fake", actor="fake", repo="fake", at="fake",
                      event_id="fake", schema_version=99, payload="fake")
        event = Event("changed", forged, "system", "owner/repo", "now")
        data = json.loads(event.to_json())
        self.assertEqual(data["payload"], forged)
        self.assertEqual((data["event"], data["actor"], data["repo"], data["at"]),
                         ("changed", "system", "owner/repo", "now"))
        self.assertEqual(uuid.UUID(hex=data["event_id"]).version, 4)
        self.assertEqual(len(data["event_id"]), 32)
        self.assertNotEqual(event.event_id, Event("changed").event_id)
        self.assertIs(type(data["schema_version"]), int)
        self.assertEqual(data["schema_version"], 1)
        self.assertTrue(is_dataclass(event))
        with self.assertRaises(FrozenInstanceError):
            event.name = "fake"

    def test_rejects_non_json_data_at_construction(self):
        cyclic = []
        cyclic.append(cyclic)
        for value in (float("nan"), float("inf"), -float("inf"), object(),
                      {1, 2}, (1, 2), b"bytes", {1: "value"}, cyclic):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises((ValueError, TypeError)):
                    Event("invalid", {"nested": [value]})
        with self.assertRaises(TypeError):
            Event("invalid", [])


class BusTests(unittest.TestCase):
    def test_registration_order_including_wildcards_and_filter(self):
        bus = EventBus()
        calls = []
        for name, label in ((None, "any1"), ("x", "x1"), ("y", "skip"),
                            (None, "any2"), ("x", "x2")):
            bus.subscribe(name, lambda e, label=label: calls.append(label))
        bus.publish(Event("x"))
        self.assertEqual(calls, ["any1", "x1", "any2", "x2"])

    def test_reentrant_publish_completes_before_outer_continues(self):
        bus = EventBus()
        calls = []

        def publish_inner(event):
            calls.append("before")
            bus.publish(Event("inner"))
            calls.append("after")

        bus.subscribe("outer", publish_inner)
        bus.subscribe(None, lambda e: calls.append(e.name))
        bus.publish(Event("outer"))
        self.assertEqual(calls, ["before", "inner", "after", "outer"])

    def test_subscription_during_delivery_uses_snapshot(self):
        bus = EventBus()
        calls = []
        bus.subscribe("x", lambda e: bus.subscribe("x", calls.append))
        bus.publish(Event("x"))
        self.assertEqual(calls, [])
        event = Event("x")
        bus.publish(event)
        self.assertEqual(calls, [event])

    def test_failure_logs_safe_identifiers_only(self):
        class Observer:
            def __call__(self, event):
                raise ValueError("synthetic-sensitive-detail")

            def __repr__(self):
                raise AssertionError("repr must never be called")

        observer = Observer()
        bus = EventBus()
        bus.subscribe(None, observer)
        calls = []
        bus.subscribe(None, calls.append)
        with patch("sys.stderr", new_callable=io.StringIO) as sink:
            bus.publish(Event("x"))
        record = json.loads(sink.getvalue())
        self.assertEqual(record["error"], "ValueError")
        self.assertEqual(record["handler"], f"{Observer.__module__}.{Observer.__qualname__}")
        self.assertNotIn("synthetic-sensitive-detail", sink.getvalue())
        self.assertEqual(len(calls), 1)

    def test_failed_audit_and_failure_sink_do_not_interrupt_observers(self):
        class BrokenSink:
            def write(self, text):
                raise OSError("sink unavailable")

        bus = EventBus()
        bus.subscribe(None, audit_to_stderr)
        calls = []
        bus.subscribe("x", calls.append)
        event = Event("x")
        with patch("sys.stderr", BrokenSink()):
            bus.publish(event)
        self.assertEqual(calls, [event])
