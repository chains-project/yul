"""Pooled HTTP client with automatic retries.

This module wraps :class:`urllib3.PoolManager`, which owns the low-level
connection pools, and :class:`urllib3.util.retry.Retry`, which drives the
retry/backoff policy.  A single ``HttpClient`` instance should be reused for
the lifetime of the process so its pools can be shared across requests.
"""

import urllib3
from urllib3.util.retry import Retry

DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = ("GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE")


def default_retry(total=5, backoff_factor=0.5, **overrides):
    """Build a :class:`Retry` with sane, overridable defaults."""
    params = dict(
        total=total,
        connect=total,
        read=total,
        redirect=3,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=DEFAULT_RETRY_STATUSES,
        allowed_methods=DEFAULT_RETRY_METHODS,
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    params.update(overrides)
    return Retry(**params)


class HttpClient:
    """A reusable, pooled HTTP client.

    Parameters
    ----------
    num_pools:
        Maximum number of distinct host pools kept in the manager's LRU cache.
    maxsize:
        Maximum number of connections retained per host pool.
    block:
        If ``True``, block when the pool is exhausted instead of discarding
        connections.
    retries:
        A :class:`~urllib3.util.retry.Retry` instance, an integer, or
        ``None``.  Defaults to :func:`default_retry`.
    timeout:
        Seconds for both connect and read, or a ``(connect, read)`` tuple, or
        a :class:`~urllib3.util.Timeout`.
    verify:
        If ``False``, skip TLS certificate verification (not recommended).
    ca_certs:
        Path to a CA bundle used to verify TLS certificates.
    headers:
        Default headers applied to every request.
    """

    def __init__(
        self,
        num_pools=10,
        maxsize=10,
        block=False,
        retries=None,
        timeout=urllib3.Timeout(connect=5.0, read=30.0),
        verify=True,
        ca_certs=None,
        headers=None,
        **connection_pool_kw,
    ):
        if retries is None:
            retries = default_retry()
        elif isinstance(retries, int):
            retries = default_retry(total=retries)

        if isinstance(timeout, (int, float)):
            timeout = urllib3.Timeout(connect=timeout, read=timeout)
        elif isinstance(timeout, tuple):
            timeout = urllib3.Timeout(connect=timeout[0], read=timeout[1])

        connection_pool_kw.setdefault("cert_reqs", "CERT_REQUIRED" if verify else "CERT_NONE")
        if ca_certs is not None:
            connection_pool_kw["ca_certs"] = ca_certs
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._manager = urllib3.PoolManager(
            num_pools=num_pools,
            headers=headers,
            maxsize=maxsize,
            block=block,
            retries=retries,
            timeout=timeout,
            **connection_pool_kw
        )

    def request(self, method, url, body=None, headers=None, **kw):
        """Perform a request, returning a :class:`urllib3.response.HTTPResponse`."""
        return self._manager.request(method, url, body=body, headers=headers, **kw)

    def get(self, url, **kw):
        return self.request("GET", url, **kw)

    def post(self, url, body=None, **kw):
        return self.request("POST", url, body=body, **kw)

    def close(self):
        """Release every pooled connection."""
        self._manager.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
