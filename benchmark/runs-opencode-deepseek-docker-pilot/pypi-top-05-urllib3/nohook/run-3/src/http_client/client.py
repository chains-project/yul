from __future__ import annotations

from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import HTTPResponse

RETRYABLE_STATUS = (429, 500, 502, 503, 504)
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


def build_pool(
    *,
    total_retries: int = 3,
    backoff_factor: float = 0.5,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
) -> PoolManager:
    """Create a PoolManager with connection reuse and retry handling.

    A single PoolManager owns the connection pools, so build it once and share
    it across the process. Requests reuse pooled connections per host and
    transparently retry on transient failures.
    """
    retries = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRYABLE_STATUS,
        allowed_methods=IDEMPOTENT_METHODS,
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    return PoolManager(
        num_pools=pool_connections,
        maxsize=pool_maxsize,
        retries=retries,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        block=False,
    )


def request(
    pool: PoolManager,
    method: str,
    url: str,
    *,
    preload_content: bool = True,
    **kwargs: object,
) -> HTTPResponse:
    """Send a request through the pool, letting urllib3 handle retries."""
    return pool.request(
        method,
        url,
        preload_content=preload_content,
        redirect=True,
        **kwargs,
    )
