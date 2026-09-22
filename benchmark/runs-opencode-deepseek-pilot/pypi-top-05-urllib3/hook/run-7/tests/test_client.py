from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from urllib3.util.retry import Retry

from http_client.client import HttpClient


class _Handler(BaseHTTPRequestHandler):
    fail_times = 0
    attempts = 0

    def do_GET(self) -> None:  # noqa: N802
        type(self).attempts += 1
        if type(self).attempts <= type(self).fail_times:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"try again")
            return
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_get_returns_body(server):
    _Handler.fail_times = 0
    _Handler.attempts = 0
    with HttpClient() as client:
        response = client.get(f"{server}/")
    assert response.status == 200
    assert response.data == b"ok"


def test_retries_on_server_error(server):
    _Handler.fail_times = 2
    _Handler.attempts = 0
    retries = Retry(total=5, status=5, backoff_factor=0.0, status_forcelist=(503,))
    with HttpClient(retries=retries) as client:
        response = client.get(f"{server}/")
    assert response.status == 200
    assert _Handler.attempts == 3
