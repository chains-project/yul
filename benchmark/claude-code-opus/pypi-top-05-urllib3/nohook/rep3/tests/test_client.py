import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from httpclient import build_pool_manager, build_retry


@pytest.fixture
def flaky_server():
    """Server that returns 503 twice, then 200."""
    state = {"hits": 0}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            state["hits"] += 1
            status, body = (503, b"busy") if state["hits"] <= 2 else (200, b"ok")
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", state
    server.shutdown()


def test_retries_until_success(flaky_server):
    url, state = flaky_server
    http = build_pool_manager(retries=build_retry(total=3, backoff_factor=0))
    resp = http.request("GET", url)
    assert resp.status == 200
    assert resp.data == b"ok"
    assert state["hits"] == 3


def test_gives_up_after_retry_budget(flaky_server):
    url, state = flaky_server
    http = build_pool_manager(retries=build_retry(total=1, backoff_factor=0))
    resp = http.request("GET", url)
    assert resp.status == 503
    assert state["hits"] == 2


def test_connections_are_reused(flaky_server):
    url, _ = flaky_server
    http = build_pool_manager(maxsize=1, retries=build_retry(total=3, backoff_factor=0))
    for _ in range(3):
        http.request("GET", url)
    pool = http.connection_from_url(url)
    assert pool.num_connections == 1
