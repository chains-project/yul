"""Pooled HTTP client with configurable retries, built on urllib3."""

from __future__ import annotations

import urllib3
from urllib3.util import Retry, Timeout


def build_retry(
    total: int = 5,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> Retry:
    """Retry policy: exponential backoff, honours Retry-After, idempotent methods only."""
    return Retry(
        total=total,
        connect=total,
        read=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=Retry.DEFAULT_ALLOWED_METHODS,
        respect_retry_after_header=True,
        raise_on_status=False,
    )


def build_pool_manager(
    num_pools: int = 10,
    maxsize: int = 10,
    block: bool = True,
    retries: Retry | None = None,
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
) -> urllib3.PoolManager:
    """Create a PoolManager.

    num_pools: number of distinct host pools kept alive.
    maxsize:   connections kept per host pool.
    block:     if True, wait for a free connection instead of opening extras
               beyond maxsize (keeps connection count bounded).
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retries if retries is not None else build_retry(),
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        headers={"User-Agent": "http-client/0.1"},
    )
