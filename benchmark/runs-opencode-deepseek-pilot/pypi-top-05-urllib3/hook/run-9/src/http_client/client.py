"""Low-level HTTP client built on urllib3.

Exposes explicit control over connection pooling and retry behaviour.
"""

from __future__ import annotations

from typing import Mapping, Optional

import urllib3
from urllib3 import PoolManager, Retry
from urllib3.response import HTTPResponse

DEFAULT_STATUS_FORCELIST = (429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"})


def build_retries(
    total: int = 5,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = DEFAULT_STATUS_FORCELIST,
) -> Retry:
    """Create a retry policy with exponential backoff.

    ``backoff_factor`` delays retries by
    ``{backoff_factor} * (2 ** (retry_number - 1))`` seconds, so the client
    backs off automatically on transient failures.
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=DEFAULT_ALLOWED_METHODS,
        respect_retry_after_header=True,
        raise_on_status=False,
    )


class HttpClient:
    """Connection-pooled HTTP client with automatic retries."""

    def __init__(
        self,
        num_pools: int = 10,
        maxsize: int = 10,
        block: bool = True,
        retries: Optional[Retry] = None,
        timeout: float = 30.0,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.retries = retries if retries is not None else build_retries()
        self.timeout = timeout
        self.headers = dict(headers or {})
        self._pool = PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=self.retries,
            headers=self.headers,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        retries: Optional[Retry] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> HTTPResponse:
        """Send a request, reusing pooled connections and retrying failures."""
        return self._pool.request(
            method,
            url,
            retries=retries if retries is not None else self.retries,
            timeout=timeout if timeout is not None else self.timeout,
            **kwargs,
        )

    def get(self, url: str, **kwargs) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def close(self) -> None:
        self._pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()


__all__ = ["HttpClient", "build_retries", "urllib3"]
