from __future__ import annotations

import threading
from collections import Counter
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from http_client import HttpClient, PoolConfig, RetryPolicy


class Handler(BaseHTTPRequestHandler):
    failures_remaining = 0
    hits: Counter[str] = Counter()
    lock = threading.Lock()

    def do_GET(self) -> None:
        with self.lock:
            Handler.hits[self.path] += 1
            if Handler.failures_remaining > 0:
                Handler.failures_remaining -= 1
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"unavailable")
                return
        body = b"ok" + self.path.encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture
def server() -> Iterator[str]:
    Handler.failures_remaining = 0
    Handler.hits = Counter()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def make_client(**retry: object) -> HttpClient:
    policy = RetryPolicy(backoff_factor=0.0, **retry)  # type: ignore[arg-type]
    return HttpClient(PoolConfig(maxsize=4, retries=policy))


def test_get_success(server: str) -> None:
    with make_client() as client:
        response = client.get(f"{server}/hello")
    assert response.status == 200
    assert response.data == b"ok/hello"


def test_retries_then_success(server: str) -> None:
    Handler.failures_remaining = 2
    with make_client(total=3) as client:
        response = client.get(f"{server}/flaky")
    assert response.status == 200
    assert Handler.hits["/flaky"] == 3


def test_retries_exhausted(server: str) -> None:
    Handler.failures_remaining = 10
    with make_client(total=2) as client:
        response = client.get(f"{server}/down")
    assert response.status == 503
    assert Handler.hits["/down"] == 3


def test_connection_pool_reused(server: str) -> None:
    with make_client() as client:
        first = client.get(f"{server}/a")
        second = client.get(f"{server}/b")
        assert first.status == second.status == 200
        pool = client._manager.connection_from_url(server)
        assert pool.num_connections == 1


def test_get_many(server: str) -> None:
    urls = [f"{server}/n/{i}" for i in range(5)]
    with make_client() as client:
        responses = client.get_many(urls, max_workers=5)
    assert [r.status for r in responses] == [200] * 5
    assert all(r.data.startswith(b"ok/n/") for r in responses)
