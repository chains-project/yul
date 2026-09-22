"""Low-level HTTP client built on urllib3.

Provides explicit control over connection pooling and automatic retries,
which the high-level ``requests`` API hides behind defaults.
"""

import urllib3
from urllib3.util.retry import Retry
from urllib3.util.timeout import Timeout

DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset(
    ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
)


def build_retry(
    total=5,
    connect=None,
    read=None,
    status=None,
    backoff_factor=0.5,
    status_forcelist=DEFAULT_RETRY_STATUSES,
    allowed_methods=DEFAULT_RETRY_METHODS,
    respect_retry_after_header=True,
    raise_on_status=True,
):
    """Build a ``Retry`` policy for transient network/server failures.

    ``backoff_factor`` makes waits grow exponentially between attempts:
    0s, 0.5s, 1s, 2s, ... (urllib3 also adds jitter).
    """
    return Retry(
        total=total,
        connect=connect,
        read=read,
        status=status,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        respect_retry_after_header=respect_retry_after_header,
        raise_on_status=raise_on_status,
    )


def build_pool_manager(
    num_pools=10,
    maxsize=10,
    block=False,
    retries=None,
    timeout=None,
    cert_reqs="CERT_REQUIRED",
):
    """Create a ``PoolManager`` with bounded connection pools.

    Each (scheme, host, port) gets its own pool holding up to ``maxsize``
    reusable connections. When a pool is exhausted and ``block`` is True,
    callers wait instead of opening extra sockets.
    """
    if retries is None:
        retries = build_retry()
    if timeout is None:
        timeout = Timeout(connect=5.0, read=30.0)

    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retries,
        timeout=timeout,
        cert_reqs=cert_reqs,
    )


class HttpClient(object):
    """Thin wrapper around ``PoolManager`` for pooled, retrying requests."""

    def __init__(self, pool_manager=None, **pool_kwargs):
        self.pool = pool_manager or build_pool_manager(**pool_kwargs)

    def request(self, method, url, body=None, headers=None, **kwargs):
        return self.pool.request(
            method,
            url,
            body=body,
            headers=headers,
            **kwargs
        )

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, body=None, **kwargs):
        return self.request("POST", url, body=body, **kwargs)

    def close(self):
        self.pool.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
