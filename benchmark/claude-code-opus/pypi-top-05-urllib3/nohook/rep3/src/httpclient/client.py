"""Pooled HTTP client built directly on urllib3."""

from __future__ import annotations

import urllib3
from urllib3.util import Retry, Timeout

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


def build_retry(
    total: int = 5,
    backoff_factor: float = 0.5,
    backoff_max: float = 30.0,
) -> Retry:
    """Retry policy: retries connect/read errors and transient status codes.

    Only idempotent methods are retried by default (urllib3's
    DEFAULT_ALLOWED_METHODS), and Retry-After headers are honoured.
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
        raise_on_status=False,
    )


def build_pool_manager(
    num_pools: int = 10,
    maxsize: int = 10,
    block: bool = True,
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
    retries: Retry | None = None,
) -> urllib3.PoolManager:
    """Create a PoolManager.

    num_pools: number of per-host connection pools kept alive.
    maxsize:   max connections kept per host pool.
    block:     if True, wait for a free connection instead of opening extras
               beyond maxsize (keeps concurrency bounded).
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        retries=retries if retries is not None else build_retry(),
    )
