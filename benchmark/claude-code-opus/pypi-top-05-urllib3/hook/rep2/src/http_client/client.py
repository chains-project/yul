"""Connection pool and retry configuration."""

from __future__ import annotations

import urllib3
from urllib3.util import Retry, Timeout


def build_retry(
    total: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> Retry:
    """Retry policy: exponential backoff, retries on transient status codes.

    Honors Retry-After headers. Only idempotent methods are retried by default.
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        respect_retry_after_header=True,
        raise_on_status=False,
    )


def build_pool_manager(
    num_pools: int = 10,
    maxsize: int = 10,
    block: bool = False,
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
    retries: Retry | None = None,
) -> urllib3.PoolManager:
    """Create a PoolManager.

    num_pools: number of per-host connection pools kept alive.
    maxsize:   max reusable connections per host pool.
    block:     if True, wait for a free connection instead of opening extras
               beyond maxsize (which are discarded after use).
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        retries=retries if retries is not None else build_retry(),
    )
