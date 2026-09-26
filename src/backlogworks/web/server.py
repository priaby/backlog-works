# Copyright (c) 2026 Pavel Riaby. All rights reserved. See LICENSE.
"""Stdlib HTTP server and router for backlog.works."""

from __future__ import annotations

import json
import socketserver
import sys
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from backlogworks.config import Config
from backlogworks.demo import DEMO_REPO, load_demo
from backlogworks.events import EventBus
from backlogworks.landing import pitch_html
from backlogworks.web.board import render_board

Response = tuple[int, bytes, str] | tuple[int, bytes, str, dict[str, str]]
Route = Callable[[], Response]

_COMMON_HEADERS = {"X-Robots-Tag": "noindex", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}
_COMMON_HEADERS["Content-Security-Policy"] = (
    "default-src 'none'; style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; img-src 'self'"
)
DEMO_SUBTITLE = "Fictitious translator product, read-only"


class App:
    """Route table plus the wiring the handler needs. One per process."""

    def __init__(self, config: Config, bus: EventBus) -> None:
        self.config = config
        self.bus = bus
        self.routes: dict[str, Route] = {
            "/": self.landing,
            "/healthz": self.healthz,
            "/demo": self.demo_board,
            "/backlog.md": self.demo_markdown,
        }

    def healthz(self) -> Response:
        return 200, b"ok", "text/plain; charset=utf-8"

    def landing(self) -> Response:
        """The landing is the demo backlog through the one board engine, with the pitch on top."""
        _, backlog = load_demo(self.bus)
        page = render_board(backlog, repo=DEMO_REPO, subtitle=DEMO_SUBTITLE, intro_html=pitch_html())
        return 200, page.encode("utf-8"), "text/html; charset=utf-8"

    def demo_board(self) -> Response:
        return 301, b"", "text/plain; charset=utf-8", {"Location": "/"}

    def demo_markdown(self) -> Response:
        markdown, _ = load_demo(self.bus)
        return 200, markdown.encode("utf-8"), "text/markdown; charset=utf-8"

    def dispatch(self, path: str) -> Response:
        route = self.routes.get(path.split("?", 1)[0])
        if route is None:
            return 404, b"not found", "text/plain; charset=utf-8"
        return route()


class Handler(BaseHTTPRequestHandler):
    app: App  # set by build_server()

    def log_message(self, format: str, *args: object) -> None:
        """Suppress stdlib diagnostics, which can contain raw request targets."""

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        """Log only method, query-free path and status, with JSON escaping."""
        try:
            print(json.dumps({"method": self.command,
                              "path": self.path.split("?", 1)[0], "status": code}),
                  file=sys.stderr, flush=True)
        except Exception:
            pass

    def _send(self, status: int, body: bytes, content_type: str,
              extra: dict[str, str] | None = None, write_body: bool = True) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for k, v in {**_COMMON_HEADERS, **(extra or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        if write_body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        self._send(*self.app.dispatch(self.path))

    def do_HEAD(self) -> None:
        self._send(*self.app.dispatch(self.path), write_body=False)


class Server(ThreadingHTTPServer):
    def server_bind(self) -> None:
        # HTTPServer.server_bind calls socket.getfqdn(), a reverse-DNS lookup
        # that stalled startup by 5 s locally. Bind directly instead.
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = host
        self.server_port = port


def build_server(config: Config, bus: EventBus) -> Server:
    Handler.app = App(config, bus)
    return Server((config.bind_host, config.port), Handler)
