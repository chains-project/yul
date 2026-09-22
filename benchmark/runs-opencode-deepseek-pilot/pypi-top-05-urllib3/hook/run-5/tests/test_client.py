from urllib3.util.retry import Retry

from http_client import HttpClient, build_pool_manager, build_retries


def test_build_retries_defaults():
    retry = build_retries(total=3, backoff_factor=1.0)
    assert isinstance(retry, Retry)
    assert retry.total == 3
    assert retry.backoff_factor == 1.0
    assert 503 in retry.status_forcelist


def test_build_pool_manager_uses_retries():
    retry = build_retries(total=2)
    pool = build_pool_manager(retries=retry, maxsize=5)
    assert pool.connection_pool_kw["maxsize"] == 5
    assert pool.connection_pool_kw["retries"] is retry


def test_client_prefixes_base_url():
    client = HttpClient(base_url="https://example.com")
    assert client.base_url == "https://example.com"
    client.close()
