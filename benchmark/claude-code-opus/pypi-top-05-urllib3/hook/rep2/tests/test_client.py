from urllib3.util import Retry

from http_client.client import build_pool_manager, build_retry


def test_retry_defaults():
    retry = build_retry()
    assert retry.total == 3
    assert 503 in retry.status_forcelist
    assert retry.respect_retry_after_header


def test_pool_manager_config():
    http = build_pool_manager(maxsize=4, block=True, retries=Retry(total=1))
    assert http.connection_pool_kw["maxsize"] == 4
    assert http.connection_pool_kw["block"] is True
    assert http.connection_pool_kw["retries"].total == 1
