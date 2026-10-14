from pytest_httpserver import HTTPServer

from httptool.client import ClientConfig, build_pool_manager


def test_retries_on_503_then_succeeds(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/flaky").respond_with_data("busy", status=503)
    httpserver.expect_ordered_request("/flaky").respond_with_data("ok", status=200)

    http = build_pool_manager(ClientConfig(backoff_factor=0))
    resp = http.request("GET", httpserver.url_for("/flaky"))

    assert resp.status == 200
    assert resp.data == b"ok"


def test_returns_final_response_when_retries_exhausted(httpserver: HTTPServer):
    httpserver.expect_request("/down").respond_with_data("nope", status=503)

    http = build_pool_manager(ClientConfig(total_retries=2, backoff_factor=0))
    resp = http.request("GET", httpserver.url_for("/down"))

    assert resp.status == 503
    assert len(httpserver.log) == 3  # 1 attempt + 2 retries


def test_connections_are_reused(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_with_data("hi")

    http = build_pool_manager(ClientConfig(maxsize=1))
    for _ in range(3):
        http.request("GET", httpserver.url_for("/"))

    pool = http.connection_from_url(httpserver.url_for("/"))
    assert pool.num_connections == 1
    assert pool.num_requests == 3
