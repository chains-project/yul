"""Low-level HTTP client built on urllib3.

Exposes connection pooling, fine-grained timeouts and automatic retries
while keeping access to the underlying urllib3 primitives.
"""

import urllib3
from urllib3.util.retry import Retry

RETRY_STATUS_CODES = (413, 429, 500, 502, 503, 504)
SAFE_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"})


def build_retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=RETRY_STATUS_CODES,
    allowed_methods=SAFE_METHODS,
):
    """Build a :class:`urllib3.util.retry.Retry` policy.

    Retries are attempted on connection errors and on the given HTTP status
    codes, with exponential backoff between attempts.
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(allowed_methods),
        raise_on_status=False,
        respect_retry_after_header=True,
    )


def build_pool_manager(
    pool_connections=10,
    pool_maxsize=10,
    retries=None,
    connect_timeout=5.0,
    read_timeout=30.0,
    block=True,
    headers=None,
):
    """Create a :class:`urllib3.PoolManager` with pooling and retries.

    ``pool_connections`` bounds the number of distinct host pools kept alive,
    while ``pool_maxsize`` bounds the number of reusable connections per host.
    """
    if retries is None:
        retries = build_retry()
    return urllib3.PoolManager(
        num_pools=pool_connections,
        maxsize=pool_maxsize,
        block=block,
        retries=retries,
        timeout=urllib3.Timeout(connect=connect_timeout, read=read_timeout),
        headers=headers,
    )


class HttpClient:
    """Thin wrapper around a pooled, retrying :class:`urllib3.PoolManager`."""

    def __init__(self, pool_manager=None, **pool_options):
        self.pool = pool_manager or build_pool_manager(**pool_options)

    def request(self, method, url, body=None, headers=None, **kwargs):
        """Perform a request, reusing pooled connections and retrying on failure."""
        return self.pool.request(
            method,
            url,
            body=body,
            headers=headers,
            redirect=kwargs.pop("redirect", True),
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
        return False
