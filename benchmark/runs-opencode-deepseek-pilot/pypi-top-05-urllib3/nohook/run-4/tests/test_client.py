import pytest

from httpclient import HttpClient, build_pool_manager, build_retry


def test_build_retry_defaults():
    retry = build_retry()
    assert retry.total == 5
    assert retry.backoff_factor == 0.5
    assert 503 in retry.status_forcelist


def test_build_retry_custom():
    retry = build_retry(total=2, backoff_factor=0.1, status_forcelist=(500,))
    assert retry.total == 2
    assert retry.backoff_factor == 0.1
    assert 500 in retry.status_forcelist


def test_pool_manager_pooling_config():
    pool = build_pool_manager(num_pools=5, maxsize=7, block=True)
    assert pool.pools._maxsize == 5
    assert pool.connection_pool_kw["maxsize"] == 7
    assert pool.connection_pool_kw["block"] is True
    assert pool.connection_pool_kw["retries"] is not None


def test_client_uses_given_pool():
    pool = build_pool_manager()
    client = HttpClient(pool_manager=pool)
    assert client.pool is pool


def test_client_close_clears_pool():
    client = HttpClient()
    client.close()
    assert len(client.pool.pools) == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
