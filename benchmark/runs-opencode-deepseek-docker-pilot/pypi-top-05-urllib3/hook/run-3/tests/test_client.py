import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from httpclient import HttpClient, build_retry


class _FlakyHandler(BaseHTTPRequestHandler):
    remaining_failures = 0

    def do_GET(self) -> None:
        if type(self).remaining_failures > 0:
            type(self).remaining_failures -= 1
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"unavailable")
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture()
def flaky_server():
    _FlakyHandler.remaining_failures = 2
    server = ThreadingHTTPServer(("127.0.0.1", 0), _FlakyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        thread.join()


def test_retries_until_success(flaky_server):
    with HttpClient(retries=build_retry(total=3, backoff_factor=0)) as client:
        response = client.get(f"{flaky_server}/")
        assert response.status == 200
        assert response.data == b"ok"
    assert _FlakyHandler.remaining_failures == 0


def test_retry_policy_is_idempotent_by_default():
    retry = build_retry(total=4, backoff_factor=1.0)
    assert retry.total == 4
    assert 503 in retry.status_forcelist
    assert "GET" in retry.allowed_methods
    assert "POST" not in retry.allowed_methods
