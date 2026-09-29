from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from http_client.client import build_retry, build_session


def test_session_mounts_pooled_adapter_and_retry_policy():
    session = build_session(pool_connections=4, pool_maxsize=7, max_retries=5, backoff_factor=0.25)
    try:
        adapter = session.get_adapter("https://example.com")
        pool_kwargs = adapter.poolmanager.connection_pool_kw
        assert pool_kwargs["maxsize"] == 7
        assert pool_kwargs["block"] is False

        retry = adapter.max_retries
        assert retry.total == 5
        assert retry.backoff_factor == 0.25
        assert set(retry.status_forcelist) == {429, 500, 502, 503, 504}
        assert "POST" not in retry.allowed_methods
    finally:
        session.close()


def test_build_retry_passes_through_per_category_limits():
    retry = build_retry(total=2, connect=1, read=3, status=4)
    assert retry.total == 2
    assert retry.connect == 1
    assert retry.read == 3
    assert retry.status == 4

    default = build_retry(total=2)
    assert default.connect is None
    assert default.read is None
    assert default.status is None


class _FlakyHandler(BaseHTTPRequestHandler):
    attempts = 0
    lock = threading.Lock()

    def do_GET(self):  # noqa: N802 - required by BaseHTTPRequestHandler
        with type(self).lock:
            type(self).attempts += 1
            attempt = type(self).attempts
        if attempt < 3:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"unavailable")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

    def log_message(self, *args):  # silence test output
        return


@pytest.fixture
def flaky_server():
    _FlakyHandler.attempts = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FlakyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def test_retries_transient_503_until_success(flaky_server):
    session = build_session(max_retries=3, backoff_factor=0)
    try:
        response = session.get(flaky_server, timeout=5)
    finally:
        session.close()

    assert response.status_code == 200
    assert _FlakyHandler.attempts == 3
