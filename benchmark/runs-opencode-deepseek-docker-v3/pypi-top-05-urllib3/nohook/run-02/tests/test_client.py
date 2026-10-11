from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from http_client import HttpClient, PoolConfig, RetryPolicy


def test_retry_policy_translates_to_urllib3() -> None:
    retry = RetryPolicy(
        total=5,
        backoff_factor=0.1,
        status_forcelist=(500, 503),
        allowed_methods=frozenset({"GET"}),
    ).to_urllib3()

    assert retry.total == 5
    assert retry.backoff_factor == 0.1
    assert retry.status_forcelist == [500, 503]
    assert retry.allowed_methods == {"GET"}


def test_pool_config_defaults_are_retry_policy() -> None:
    assert isinstance(PoolConfig().retries, RetryPolicy)


def test_client_is_a_context_manager() -> None:
    with HttpClient() as client:
        assert client.pool_config.maxsize == 10


class _FlakyHandler(BaseHTTPRequestHandler):
    failures_remaining = 2
    hits = 0
    lock = threading.Lock()

    def do_GET(self) -> None:  # noqa: N802
        with self.lock:
            type(self).hits += 1
            fail = type(self).failures_remaining > 0
            if fail:
                type(self).failures_remaining -= 1
        status = 500 if fail else 200
        self.send_response(status)
        self.end_headers()
        self.wfile.write(b"ok" if not fail else b"boom")

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def flaky_server() -> str:
    _FlakyHandler.hits = 0
    _FlakyHandler.failures_remaining = 2
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FlakyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/"
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.enable_socket
def test_retries_until_success(flaky_server: str) -> None:
    policy = RetryPolicy(total=3, backoff_factor=0.0)
    with HttpClient(pool=PoolConfig(retries=policy), timeout=2.0) as client:
        response = client.get(flaky_server)
        assert response.status == 200
        assert response.data == b"ok"
        response.release_conn()

    assert _FlakyHandler.hits == 3


@pytest.mark.enable_socket
def test_no_retry_when_disabled(flaky_server: str) -> None:
    with HttpClient(pool=PoolConfig(retries=RetryPolicy(total=0)), timeout=2.0) as client:
        response = client.get(flaky_server)
        assert response.status == 500
        response.release_conn()

    assert _FlakyHandler.hits == 1
