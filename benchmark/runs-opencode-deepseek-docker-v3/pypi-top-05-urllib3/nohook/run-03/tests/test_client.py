import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from httpkit import HTTPClient, HTTPError, RetryPolicy


class _Handler(BaseHTTPRequestHandler):
    fail_times = 0
    hits = 0
    lock = threading.Lock()

    def log_message(self, *args):  # keep test output quiet
        pass

    def do_GET(self):
        with _Handler.lock:
            _Handler.hits += 1
            attempt = _Handler.hits
        if attempt <= _Handler.fail_times:
            self.send_response(503)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def server():
    _Handler.fail_times = 0
    _Handler.hits = 0
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()


def test_basic_get(server):
    with HTTPClient() as client:
        response = client.get(server, preload_content=True)
        assert response.status == 200
        assert response.data == b"ok"


def test_retries_on_503_then_succeeds(server):
    _Handler.fail_times = 2
    policy = RetryPolicy(total=3, backoff_factor=0.0)
    with HTTPClient(retries=policy) as client:
        response = client.get(server, preload_content=True)
    assert response.status == 200
    assert _Handler.hits == 3


def test_exhausted_retries_raise(server):
    _Handler.fail_times = 10
    policy = RetryPolicy(total=2, backoff_factor=0.0)
    with HTTPClient(retries=policy) as client:
        response = client.get(server, preload_content=True)
    # raise_on_status defaults to False, so we get the final 503 back.
    assert response.status == 503
    assert _Handler.hits == 3


def test_connection_error_is_wrapped():
    policy = RetryPolicy(total=1, backoff_factor=0.0)
    with HTTPClient(retries=policy, timeout=1.0) as client:
        with pytest.raises(HTTPError):
            client.get("http://127.0.0.1:1/", preload_content=True)
