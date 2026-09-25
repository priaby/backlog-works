"""Minimal, dependency-free web service for backlog.works.

Serves a "coming soon" placeholder page and a health check. Uses only the
Python standard library so the container build has no dependency surface.
"""

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>backlog.works -- coming soon</title>
<style>
  body { font-family: sans-serif; max-width: 40em; margin: 4em auto; padding: 0 1em; color: #222; }
  h1 { font-size: 1.5em; }
</style>
</head>
<body>
<h1>backlog.works</h1>
<p>Coming soon.</p>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8")
            return
        if self.path == "/":
            self._send(200, INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        # Keep default stderr logging (Railway captures container logs);
        # override left in place only to document intent.
        super().log_message(fmt, *args)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
