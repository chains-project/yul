"""Pooled HTTP client built directly on urllib3."""

from __future__ import annotations

import urllib3
from urllib3.util import Retry, Timeout

# Status codes worth retrying: rate limiting and transient server errors.
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


def build_retry(
    total: int = 5,
    backoff_factor: float = 0.5,
    backoff_max: float = 30.0,
) -> Retry:
    """Retry policy with exponential backoff that honors Retry-After headers.

    Retries on connection errors, read errors, and RETRY_STATUSES. Methods
    default to urllib3's idempotent set, so POST is never retried implicitly.
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        backoff_max=backoff_max,
        status_forcelist=RETRY_STATUSES,
        respect_retry_after_header=True,
        raise_on_status=False,  # Return the final response instead of raising.
    )


def build_pool_manager(
    num_pools: int = 10,
    maxsize: int = 10,
    block: bool = True,
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
    retries: Retry | None = None,
) -> urllib3.PoolManager:
    """Create a PoolManager that keeps one connection pool per host.

    num_pools: how many host pools to cache before evicting the oldest.
    maxsize:   connections kept alive per host pool.
    block:     if True, wait for a free connection instead of opening extras
               beyond maxsize (caps concurrency per host).
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        retries=retries if retries is not None else build_retry(),
        headers={"User-Agent": "httpclient/0.1"},
    )
