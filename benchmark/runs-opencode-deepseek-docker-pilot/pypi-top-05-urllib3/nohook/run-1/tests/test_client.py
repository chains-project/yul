from __future__ import annotations

from netclient import PooledHTTPClient, RetryConfig, TimeoutConfig


def test_retry_config_build() -> None:
    retry = RetryConfig(total=4, backoff_factor=0.1).build()
    assert retry.total == 4
    assert retry.backoff_factor == 0.1
    assert 503 in retry.status_forcelist
    assert "GET" in retry.allowed_methods
    assert "POST" not in retry.allowed_methods


def test_timeout_config_build() -> None:
    timeout = TimeoutConfig(connect=1.0, read=2.0).build()
    assert timeout.connect_timeout == 1.0
    assert timeout.read_timeout == 2.0


def test_successful_get(httpserver) -> None:
    httpserver.expect_request("/hello").respond_with_data("world")
    with PooledHTTPClient() as client:
        response = client.get(httpserver.url_for("/hello"))
    assert response.status == 200
    assert response.data == b"world"


def test_retries_on_server_error(httpserver) -> None:
    httpserver.expect_oneshot_request("/flaky").respond_with_data("busy", status=503)
    httpserver.expect_oneshot_request("/flaky").respond_with_data("busy", status=503)
    httpserver.expect_request("/flaky").respond_with_data("ok")

    with PooledHTTPClient(retries=RetryConfig(total=3, backoff_factor=0.0)) as client:
        response = client.get(httpserver.url_for("/flaky"))

    assert response.status == 200
    assert response.data == b"ok"
    assert len(httpserver.log) == 3


def test_retries_can_be_overridden_per_request(httpserver) -> None:
    httpserver.expect_request("/down").respond_with_data("down", status=503)
    with PooledHTTPClient(retries=RetryConfig(total=3, backoff_factor=0.0)) as client:
        response = client.get(httpserver.url_for("/down"), retries=RetryConfig(total=0))
    assert response.status == 503
    assert len(httpserver.log) == 1
