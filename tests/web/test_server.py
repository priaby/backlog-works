# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""HTTP access logging tests without sockets."""

import io
import json
import unittest
from unittest.mock import Mock, patch

from backlogworks import __main__ as entry
from backlogworks.config import Config
from backlogworks.demo import load_demo
from backlogworks.events import EventBus
from backlogworks.landing import pitch_html
from backlogworks.web.server import App, Handler, build_server


class RouteTests(unittest.TestCase):
    def test_source_route_returns_exact_demo_markdown(self):
        markdown, _ = load_demo()
        response = App(Config(), EventBus()).dispatch('/backlog.md?cache=ignored')
        self.assertEqual(response, (200, markdown.encode('utf-8'), 'text/markdown; charset=utf-8'))

    def test_root_contains_pitch_and_board(self):
        status, body, content_type = App(Config(), EventBus()).dispatch('/')
        self.assertEqual((status, content_type), (200, 'text/html; charset=utf-8'))
        page = body.decode('utf-8')
        self.assertIn(pitch_html(), page)
        self.assertIn('id="board"', page)
        self.assertLess(page.index(pitch_html()), page.index('id="board"'))
        self.assertIn('href="/backlog.md"', page)
        self.assertIn('id="U611"', page)
        self.assertNotIn('PBI-', page)
        self.assertEqual(page.count(' data-view="'), 4)
        for removed in ('view-count', 'job-filter', 'empty-state', 'bug-row', '<details'):
            self.assertNotIn(removed, page)

    def test_response_headers_and_head_without_sockets(self):
        handler = Handler.__new__(Handler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = io.BytesIO()
        handler._send(200, b'body', 'text/html; charset=utf-8', write_body=False)
        headers = dict(call.args for call in handler.send_header.call_args_list)
        self.assertEqual(headers['Content-Security-Policy'],
                         "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self'")
        self.assertEqual(headers['X-Robots-Tag'], 'noindex')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(headers['Content-Length'], '4')
        self.assertEqual(handler.wfile.getvalue(), b'')


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
        status, body, _ = App(Config(), EventBus()).dispatch("/")[:3]
        self.assertEqual(status, 200)
        self.assertIn(b"Fictitious translator product, read-only", body)
