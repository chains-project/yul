"""Build ``requests.Session`` objects tuned for pooled, retrying traffic.

The session returned by :func:`build_session` mounts a single
``HTTPAdapter`` on both ``http://`` and ``https://`` so every request shares
the adapter's connection pools. Retries are handled by ``urllib3`` at the
transport layer, which lets it retry failed *connections* (not just responses)
and honour ``Retry-After`` headers.
"""

from __future__ import annotations

from collections.abc import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_POOL_CONNECTIONS = 10
DEFAULT_POOL_MAXSIZE = 10
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_FACTOR = 0.5
DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS = ("HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE")
DEFAULT_TIMEOUT = 10.0


def build_session(
    *,
    pool_connections: int = DEFAULT_POOL_CONNECTIONS,
    pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    status_forcelist: Iterable[int] = DEFAULT_RETRY_STATUSES,
    allowed_methods: Iterable[str] = DEFAULT_ALLOWED_METHODS,
    pool_block: bool = False,
) -> requests.Session:
    """Return a session with a pooled, retrying transport.

    Args:
        pool_connections: Number of distinct host pools to cache.
        pool_maxsize: Maximum connections kept per pool.
        max_retries: Total retry attempts across connect/read/status.
        backoff_factor: Base for exponential sleep ``{backoff_factor} *
            (2 ** (retry - 1))`` between attempts. ``0`` disables sleeping.
        status_forcelist: Response codes that trigger a retry.
        allowed_methods: HTTP methods that may be retried.
        pool_block: Block when the pool is exhausted instead of discarding the
            oldest connection.

    Returns:
        A ``requests.Session`` whose adapters share the configured pools.
    """
    retry = Retry(
        total=max_retries,
        connect=max_retries,
        read=max_retries,
        status=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=tuple(status_forcelist),
        allowed_methods=frozenset(allowed_methods),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        max_retries=retry,
        pool_block=pool_block,
    )
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
