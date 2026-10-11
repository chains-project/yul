from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from urllib3 import Retry
from urllib3.exceptions import MaxRetryError

from http_script.client import HttpClient, build_retry


class Handler(BaseHTTPRequestHandler):
    ok_hits = 0
    flaky_hits = 0

    def do_GET(self) -> None:
        if self.path == "/ok":
            Handler.ok_hits += 1
            self._respond(200, b"ok")
        elif self.path == "/flaky":
            Handler.flaky_hits += 1
            if Handler.flaky_hits < 3:
                self._respond(503, b"unavailable")
            else:
                self._respond(200, b"recovered")
        else:
            self._respond(404, b"not found")

    def _respond(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture()
def server() -> Iterator[str]:
    Handler.ok_hits = 0
    Handler.flaky_hits = 0
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        httpd.shutdown()
        thread.join()
        httpd.server_close()


def test_build_retry_defaults() -> None:
    retry = build_retry(total=3)
    assert isinstance(retry, Retry)
    assert retry.total == 3
    assert retry.connect == 3
    assert retry.read == 3
    assert 503 in retry.status_forcelist


def test_build_retry_clamps_negative() -> None:
    assert build_retry(total=-1).total == 0


def test_get_returns_body(server: str) -> None:
    with HttpClient(retries=build_retry(total=0)) as client:
        response = client.get(f"{server}/ok")
    assert response.status == 200
    assert response.data == b"ok"


def test_retries_status_until_success(server: str) -> None:
    retries = build_retry(total=5, backoff_factor=0.0)
    with HttpClient(retries=retries) as client:
        response = client.get(f"{server}/flaky")
    assert response.status == 200
    assert response.data == b"recovered"
    assert Handler.flaky_hits == 3


def test_raises_after_exhausting_retries(server: str) -> None:
    retries = build_retry(
        total=1, backoff_factor=0.0, status_forcelist=(503,), raise_on_status=True
    )
    with HttpClient(retries=retries) as client:
        with pytest.raises(MaxRetryError):
            client.get(f"{server}/flaky")
