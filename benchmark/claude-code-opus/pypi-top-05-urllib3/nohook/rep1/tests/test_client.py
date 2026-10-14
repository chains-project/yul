from werkzeug import Response

from httpclient.client import build_pool_manager, build_retry


def test_retries_transient_errors(httpserver):
    httpserver.expect_ordered_request("/flaky").respond_with_data("", status=503)
    httpserver.expect_ordered_request("/flaky").respond_with_data("ok")

    http = build_pool_manager(retries=build_retry(total=3, backoff_factor=0))
    resp = http.request("GET", httpserver.url_for("/flaky"))

    assert resp.status == 200
    assert resp.data == b"ok"
    assert len(resp.retries.history) == 1


def test_returns_final_response_when_retries_exhausted(httpserver):
    httpserver.expect_request("/down").respond_with_data("", status=503)

    http = build_pool_manager(retries=build_retry(total=2, backoff_factor=0))
    resp = http.request("GET", httpserver.url_for("/down"))

    assert resp.status == 503
    assert len(resp.retries.history) == 2


def test_post_is_not_retried(httpserver):
    httpserver.expect_request("/submit", method="POST").respond_with_data("", status=503)

    http = build_pool_manager(retries=build_retry(total=3, backoff_factor=0))
    resp = http.request("POST", httpserver.url_for("/submit"), body=b"x")

    assert resp.status == 503
    assert len(httpserver.log) == 1


def test_connections_are_reused(httpserver):
    httpserver.expect_request("/").respond_with_response(Response("hi"))

    http = build_pool_manager(maxsize=1)
    for _ in range(3):
        assert http.request("GET", httpserver.url_for("/")).status == 200

    pool = http.connection_from_url(httpserver.url_for("/"))
    assert pool.num_connections == 1
    assert pool.num_requests == 3
