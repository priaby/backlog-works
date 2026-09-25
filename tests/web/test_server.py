# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""HTTP access logging tests without sockets."""

import io
import json
import unittest
from unittest.mock import Mock, patch

from backlogworks import __main__ as entry
from backlogworks.config import Config
from backlogworks.events import EventBus
from backlogworks.web.server import App, Handler, build_server


class LoggingTests(unittest.TestCase):
    def test_access_logs_only_method_path_status(self):
        handler = Handler.__new__(Handler)
        handler.command = "GET"
        handler.path = "/signin?token=synthetic-sensitive-detail"
        with patch("sys.stderr", new_callable=io.StringIO) as sink:
            handler.log_request(200, 123)
            handler.log_message("bad request %s", handler.path)
            handler.log_error("bad request %s", handler.path)
        self.assertEqual(json.loads(sink.getvalue()),
                         {"method": "GET", "path": "/signin", "status": 200})
        self.assertNotIn("synthetic-sensitive-detail", sink.getvalue())

    def test_access_log_escapes_control_characters(self):
        handler = Handler.__new__(Handler)
        handler.command = "GET"
        handler.path = "/path\nforged?secret=hidden"
        with patch("sys.stderr", new_callable=io.StringIO) as sink:
            handler.log_request(404)
        self.assertEqual(len(sink.getvalue().splitlines()), 1)
        self.assertEqual(json.loads(sink.getvalue())["path"], "/path\nforged")


class StartupTests(unittest.TestCase):
    def test_composition_publishes_after_construction_before_serving(self):
        calls = []
        bus = EventBus()
        bus.subscribe(None, lambda event: calls.append(event))
        server = Mock(server_port=8123)

        class ServerContext:
            def __enter__(self):
                return server

            def __exit__(self, *args):
                calls.append("closed")

        def construct(config, passed_bus):
            self.assertIs(passed_bus, bus)
            calls.append("constructed")
            return ServerContext()

        server.serve_forever.side_effect = lambda: calls.append("serving")
        with patch.object(entry.Config, "from_env"), patch.object(entry, "build_bus", return_value=bus):
            with patch.object(entry, "build_server", side_effect=construct):
                entry.main()
        self.assertEqual(calls[0], "constructed")
        self.assertEqual(calls[1].name, "service.started")
        self.assertEqual(calls[1].payload, {"port": 8123})
        self.assertEqual(calls[2:], ["serving", "closed"])

    def test_server_construction_does_not_publish_or_serve(self):
        bus = EventBus()
        seen = []
        bus.subscribe(None, seen.append)
        config = Config()
        with patch("backlogworks.web.server.Server") as server:
            result = build_server(config, bus)
        server.assert_called_once_with((config.bind_host, config.port), Handler)
        self.assertIs(result, server.return_value)
        result.serve_forever.assert_not_called()
        self.assertEqual(seen, [])

    def test_demo_route_identifies_fictitious_read_only_product(self):
        status, body, _ = App(Config(), EventBus()).dispatch("/demo")
        self.assertEqual(status, 200)
        self.assertIn(b"Fictitious translator product, read-only", body)
