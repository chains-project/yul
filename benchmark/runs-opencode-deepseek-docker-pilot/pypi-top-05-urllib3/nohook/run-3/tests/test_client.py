from urllib3 import PoolManager, Retry

from http_client.client import RETRYABLE_STATUS, build_pool


def test_build_pool_returns_configured_manager() -> None:
    pool = build_pool(total_retries=5, pool_maxsize=4)

    assert isinstance(pool, PoolManager)
    assert isinstance(pool.connection_pool_kw["retries"], Retry)
    assert pool.connection_pool_kw["retries"].total == 5


def test_retryable_status_codes_cover_transient_failures() -> None:
    assert 503 in RETRYABLE_STATUS
    assert 429 in RETRYABLE_STATUS
    assert 404 not in RETRYABLE_STATUS
