"""Tests for the pooled HTTP client using a local threaded HTTP server."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import urllib3

from http_client import HttpClient


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.requests = 0
        self.fail_until = 0
        self.client_ports: list[int] = []


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    state: _State

    def do_GET(self) -> None:  # noqa: N802
        with self.state.lock:
            self.state.requests += 1
            self.state.client_ports.append(self.client_address[1])
            should_fail = self.state.requests <= self.state.fail_until

        if should_fail:
            self.send_response(503)
            body = b"try again"
        else:
            self.send_response(200)
            body = b"ok"

        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:  # silence test output
        pass


@pytest.fixture()
def server() -> tuple[str, _State]:
    state = _State()
    _Handler.state = state
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    try:
        yield f"http://{host}:{port}/", state
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def test_get_returns_ok(server: tuple[str, _State]) -> None:
    url, state = server
    with HttpClient() as client:
        response = client.get(url)
    assert response.status == 200
    assert response.data == b"ok"
    assert state.requests == 1


def test_retries_on_503(server: tuple[str, _State]) -> None:
    url, state = server
    state.fail_until = 2
    with HttpClient(total_retries=3, backoff_factor=0) as client:
        response = client.get(url)
    assert response.status == 200
    assert state.requests == 3


def test_exhausted_retries_returns_last_response(server: tuple[str, _State]) -> None:
    url, state = server
    state.fail_until = 99
    with HttpClient(total_retries=2, backoff_factor=0) as client:
        response = client.get(url)
    assert response.status == 503
    assert state.requests == 3


def test_exhausted_retries_can_raise(server: tuple[str, _State]) -> None:
    url, state = server
    state.fail_until = 99
    with HttpClient(total_retries=1, backoff_factor=0, raise_on_status=True) as client:
        with pytest.raises(urllib3.exceptions.MaxRetryError):
            client.get(url)
    assert state.requests == 2


def test_connections_are_reused(server: tuple[str, _State]) -> None:
    url, state = server
    with HttpClient() as client:
        for _ in range(3):
            client.get(url)
    assert state.requests == 3
    assert len(set(state.client_ports)) == 1
