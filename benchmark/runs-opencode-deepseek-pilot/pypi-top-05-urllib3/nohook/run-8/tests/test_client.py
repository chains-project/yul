import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import pytest

from httpkit import HttpClient, default_retries


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    failures = 0
    seen_connections = []

    def log_message(self, *args):
        pass

    def do_GET(self):
        Handler.seen_connections.append(self.client_address)
        if Handler.failures > 0:
            Handler.failures -= 1
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"unavailable")
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


@pytest.fixture
def server():
    Handler.failures = 0
    Handler.seen_connections = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    host, port = httpd.server_address
    yield "http://{}:{}".format(host, port)
    httpd.shutdown()
    httpd.server_close()


def test_get_succeeds(server):
    with HttpClient() as client:
        response = client.get(server + "/")
    assert response.status == 200
    assert response.data == b"ok"


def test_retries_on_503(server):
    Handler.failures = 2
    client = HttpClient(retries=default_retries(total=3, backoff_factor=0.01))
    try:
        response = client.get(server + "/")
    finally:
        client.close()
    assert response.status == 200


def test_retries_exhausted_returns_status(server):
    Handler.failures = 5
    client = HttpClient(retries=default_retries(total=2, backoff_factor=0.01))
    try:
        response = client.get(server + "/")
    finally:
        client.close()
    assert response.status == 503
    assert len(Handler.seen_connections) == 3


def test_connection_is_pooled(server):
    with HttpClient() as client:
        client.get(server + "/")
        client.get(server + "/")
    assert len(Handler.seen_connections) == 2
