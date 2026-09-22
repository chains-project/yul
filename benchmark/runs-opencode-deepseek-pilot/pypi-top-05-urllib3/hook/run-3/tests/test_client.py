"""Tests for the pooling/retrying HTTP client."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from httpclient import HttpClient, build_default_client


class _Handler(BaseHTTPRequestHandler):
    fail_first = 0
    requests = 0

    def do_GET(self) -> None:  # noqa: N802
        type(self).requests += 1
        if type(self).requests <= type(self).fail_first:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"unavailable")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args: object) -> None:  # silence
        pass


@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    yield f"http://{host}:{port}"
    httpd.shutdown()
    thread.join()


@pytest.fixture(autouse=True)
def _reset_handler():
    _Handler.fail_first = 0
    _Handler.requests = 0
    yield


def test_get_returns_response(server):
    with HttpClient(max_retries=0) as client:
        resp = client.get(server + "/")
    assert resp.status == 200
    assert resp.data == b"ok"
    assert _Handler.requests == 1


def test_retries_on_retryable_status(server):
    _Handler.fail_first = 2
    client = HttpClient(
        max_retries=3,
        backoff_factor=0,
        retry_statuses=(503,),
    )
    try:
        resp = client.get(server + "/")
    finally:
        client.close()
    assert resp.status == 200
    assert _Handler.requests == 3


def test_gives_up_after_max_retries(server):
    _Handler.fail_first = 10
    client = HttpClient(max_retries=2, backoff_factor=0, retry_statuses=(503,))
    try:
        resp = client.get(server + "/")
    finally:
        client.close()
    assert resp.status == 503
    assert _Handler.requests == 3


def test_default_client_has_retries_configured():
    client = build_default_client()
    try:
        assert client._retries.total == 3
        assert 503 in client._retries.status_forcelist
    finally:
        client.close()
