import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from http_client import HttpClient
from http_client.client import build_retries


@pytest.fixture
def flaky_server():
    state = {"hits": 0, "fail_until": 3}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state["hits"] += 1
            if state["hits"] < state["fail_until"]:
                self.send_response(503)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/", state
    finally:
        server.shutdown()
        thread.join()


def test_retries_on_status(flaky_server):
    url, state = flaky_server
    with HttpClient(retries=build_retries(total=5, backoff_factor=0.0)) as client:
        resp = client.get(url)
    assert resp.status == 200
    assert state["hits"] == 3


def test_connection_is_reused(flaky_server):
    url, state = flaky_server
    with HttpClient() as client:
        for _ in range(3):
            client.get(url)
    assert state["hits"] == 5
