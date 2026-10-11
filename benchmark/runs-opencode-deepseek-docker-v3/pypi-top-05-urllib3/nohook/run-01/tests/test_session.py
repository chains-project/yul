from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from resilient_http import build_session


def test_mounts_shared_adapter_on_http_and_https() -> None:
    session = build_session()
    http = session.get_adapter("http://example.com")
    https = session.get_adapter("https://example.com")
    assert isinstance(http, HTTPAdapter)
    assert http is https


def test_adapter_pool_configuration() -> None:
    session = build_session(pool_connections=3, pool_maxsize=7, pool_block=True)
    adapter = session.get_adapter("https://example.com")
    assert adapter._pool_connections == 3
    assert adapter._pool_maxsize == 7
    assert adapter._pool_block is True


def test_retry_configuration() -> None:
    session = build_session(
        max_retries=4,
        backoff_factor=0.25,
        status_forcelist=(503,),
        allowed_methods=("GET",),
    )
    retry = session.get_adapter("https://example.com").max_retries
    assert isinstance(retry, Retry)
    assert retry.total == 4
    assert retry.connect == 4
    assert retry.read == 4
    assert retry.status == 4
    assert retry.backoff_factor == 0.25
    assert set(retry.status_forcelist) == {503}
    assert retry.allowed_methods == frozenset({"GET"})
    assert retry.respect_retry_after_header is True


class _FlakyHandler(BaseHTTPRequestHandler):
    failures = 2
    attempts = 0

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        type(self).attempts += 1
        if type(self).attempts <= type(self).failures:
            self.send_response(503)
            self.end_headers()
            return
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture()
def flaky_server() -> Iterator[str]:
    _FlakyHandler.attempts = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FlakyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_retries_transient_failures_then_succeeds(flaky_server: str) -> None:
    session = build_session(max_retries=3, backoff_factor=0)
    response = session.get(flaky_server, timeout=2)

    assert response.status_code == 200
    assert response.text == "ok"
    assert _FlakyHandler.attempts == 3
