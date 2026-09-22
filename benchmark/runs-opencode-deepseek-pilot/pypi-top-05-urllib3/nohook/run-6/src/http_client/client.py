"""Low-level HTTP client built on top of urllib3.

Provides connection pooling and configurable automatic retries with
exponential backoff, while still exposing the raw urllib3 response object
for callers that need fine-grained control.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Sequence

import urllib3
from urllib3 import PoolManager, Retry
from urllib3.response import HTTPResponse

DEFAULT_STATUS_FORCELIST: Sequence[int] = (429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS = frozenset(
    {"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"}
)


class HttpClient:
    """A pooled HTTP client with automatic retries.

    The underlying :class:`urllib3.PoolManager` keeps a pool of connections
    per host, so repeated requests to the same origin reuse TCP connections
    instead of performing a full handshake every time.

    Args:
        pool_connections: Number of distinct host pools to cache.
        max_pool_size: Maximum number of connections to keep per host pool.
        block: If ``True``, block when the pool is exhausted instead of
            raising ``EmptyPoolError``.
        total_retries: Total number of retries across connect/read/status.
        backoff_factor: Multiplier for exponential backoff between retries.
        backoff_max: Upper bound on the backoff delay, in seconds.
        status_forcelist: Response status codes that should be retried.
        allowed_methods: HTTP methods eligible for retry.
        raise_on_status: Raise ``MaxRetryError`` when retries are exhausted
            due to a retryable status code.
        timeout: Default timeout (connect and read) in seconds.
        headers: Default headers sent with every request.
        **pool_kwargs: Extra keyword arguments forwarded to ``PoolManager``.
    """

    def __init__(
        self,
        *,
        pool_connections: int = 10,
        max_pool_size: int = 10,
        block: bool = False,
        total_retries: int = 3,
        connect_retries: Optional[int] = None,
        read_retries: Optional[int] = None,
        backoff_factor: float = 0.5,
        backoff_max: float = 60.0,
        status_forcelist: Iterable[int] = DEFAULT_STATUS_FORCELIST,
        allowed_methods: Iterable[str] = DEFAULT_ALLOWED_METHODS,
        raise_on_status: bool = False,
        timeout: float = 10.0,
        headers: Optional[Mapping[str, str]] = None,
        **pool_kwargs: Any,
    ) -> None:
        self.timeout = timeout
        self.retries = Retry(
            total=total_retries,
            connect=connect_retries,
            read=read_retries,
            redirect=total_retries,
            status=total_retries,
            backoff_factor=backoff_factor,
            backoff_max=backoff_max,
            status_forcelist=tuple(status_forcelist),
            allowed_methods=frozenset(m.upper() for m in allowed_methods),
            raise_on_status=raise_on_status,
            respect_retry_after_header=True,
        )
        self.pool = PoolManager(
            num_pools=pool_connections,
            maxsize=max_pool_size,
            block=block,
            retries=self.retries,
            timeout=urllib3.Timeout(connect=timeout, read=timeout),
            headers=dict(headers) if headers else None,
            **pool_kwargs,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        retries: Optional[Retry] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> HTTPResponse:
        """Perform a request and return the raw urllib3 response.

        Extra keyword arguments are passed straight through to
        :meth:`urllib3.PoolManager.request`, allowing low-level control
        (``fields``, ``body``, ``redirect``, ``preload_content``, ...).
        """
        if timeout is not None:
            kwargs["timeout"] = urllib3.Timeout(connect=timeout, read=timeout)
        if retries is not None:
            kwargs["retries"] = retries
        return self.pool.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Close all pooled connections and release resources."""
        self.pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
