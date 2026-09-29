from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from urllib3 import Retry

from httpclient import HTTPClient


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _respond(self, status: int, body: bytes = b"") -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        state = self.server.state
        state["attempts"] += 1
        state["peers"].append(self.client_address[1])
        if state["attempts"] <= state["fail_until"]:
            self._respond(503, b"unavailable")
            return
        self._respond(200, b"ok")

    def log_message(self, *args) -> None:
        pass


@pytest.fixture
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    httpd.state = {"attempts": 0, "fail_until": 0, "peers": []}
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def _url(server) -> str:
    return f"http://127.0.0.1:{server.server_port}/"


def test_retries_transient_status_until_success(server):
    server.state["fail_until"] = 2
    retries = Retry(
        total=5,
        status_forcelist=(503,),
        backoff_factor=0.05,
        raise_on_status=False,
    )
    with HTTPClient(retries=retries) as client:
        response = client.get(_url(server))
    assert response.status == 200
    assert response.data == b"ok"
    assert server.state["attempts"] == 3


def test_returns_final_response_after_exhausting_retries(server):
    server.state["fail_until"] = 10
    retries = Retry(
        total=2,
        status_forcelist=(503,),
        backoff_factor=0.05,
        raise_on_status=False,
    )
    with HTTPClient(retries=retries) as client:
        response = client.get(_url(server))
    assert response.status == 503
    assert server.state["attempts"] == 3


def test_reuses_pooled_connection(server):
    with HTTPClient() as client:
        client.get(_url(server))
        client.get(_url(server))
    assert server.state["attempts"] == 2
    assert len(set(server.state["peers"])) == 1


def test_base_url_is_prepended(server):
    retries = Retry(total=0, raise_on_status=False)
    with HTTPClient(f"{_url(server)}", retries=retries) as client:
        response = client.get("path")
    assert response.status == 200
