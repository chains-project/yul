from urllib3.util import Retry

from http_client.client import build_pool_manager, build_retry


def test_retry_defaults():
    retry = build_retry()
    assert isinstance(retry, Retry)
    assert retry.total == 5
    assert 503 in retry.status_forcelist
    assert retry.respect_retry_after_header


def test_pool_manager_config():
    http = build_pool_manager(maxsize=4, retries=build_retry(total=2))
    assert http.connection_pool_kw["maxsize"] == 4
    assert http.connection_pool_kw["block"] is True
    assert http.connection_pool_kw["retries"].total == 2


def test_connections_are_reused_per_host():
    http = build_pool_manager()
    a = http.connection_from_url("https://example.com/a")
    b = http.connection_from_url("https://example.com/b")
    assert a is b
