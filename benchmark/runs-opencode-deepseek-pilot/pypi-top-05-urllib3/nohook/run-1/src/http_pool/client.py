"""Connection-pooled, retrying HTTP client.

The client wraps :class:`urllib3.PoolManager` so that a single instance keeps
a pool of reusable connections per host, and :class:`urllib3.util.Retry` so
transient failures (connection errors and retryable status codes) are retried
with exponential backoff.
"""

from __future__ import annotations

from typing import Any, Mapping

import urllib3
from urllib3 import PoolManager, Retry
from urllib3.response import HTTPResponse

DEFAULT_TIMEOUT = 10.0

#: Methods that are safe to replay automatically. Non-idempotent methods such
#: as POST are intentionally excluded unless the caller opts in.
RETRYABLE_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"})

#: HTTP status codes that almost always represent a transient condition.
RETRYABLE_STATUSES = frozenset({413, 429, 500, 502, 503, 504})

#: Retry policy shared by every :class:`HttpClient` unless overridden:
#: up to 3 attempts, exponential backoff, honouring ``Retry-After``.
DEFAULT_RETRY = Retry(
    total=3,
    connect=3,
    read=3,
    redirect=3,
    status=3,
    backoff_factor=0.5,
    status_forcelist=sorted(RETRYABLE_STATUSES),
    allowed_methods=RETRYABLE_METHODS,
    respect_retry_after_header=True,
    raise_on_status=False,
)


class HTTPError(Exception):
    """Raised when a request cannot be completed successfully."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class HttpClient:
    """A reusable, connection-pooled HTTP client.

    Args:
        retries: Retry policy. Defaults to :data:`DEFAULT_RETRY`.
        pool_connections: Number of distinct host pools to cache.
        pool_maxsize: Maximum number of connections to keep per host pool.
        block: If ``True``, block for a free connection instead of raising
            when a pool is exhausted.
        timeout: Default timeout in seconds applied to every request.
        headers: Default headers sent with every request.
    """

    def __init__(
        self,
        *,
        retries: Retry | int | None = DEFAULT_RETRY,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        block: bool = False,
        timeout: float | None = DEFAULT_TIMEOUT,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.timeout = timeout
        self._pool = PoolManager(
            num_pools=pool_connections,
            maxsize=pool_maxsize,
            block=block,
            retries=retries,
            headers=dict(headers) if headers else None,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        fields: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        retries: Retry | int | None = None,
        preload_content: bool = True,
        decode_content: bool = True,
    ) -> HTTPResponse:
        """Perform a request, retrying transient failures.

        Returns the :class:`~urllib3.response.HTTPResponse`. Raises
        :class:`HTTPError` for network failures and for status codes that are
        still >= 400 after retries are exhausted.
        """
        try:
            response = self._pool.request(
                method,
                url,
                body=body,
                fields=fields,
                headers=dict(headers) if headers else None,
                timeout=self.timeout if timeout is None else timeout,
                retries=retries,
                preload_content=preload_content,
                decode_content=decode_content,
            )
        except urllib3.exceptions.HTTPError as exc:
            raise HTTPError(f"{method} {url} failed: {exc}") from exc

        if response.status >= 400:
            raise HTTPError(
                f"{method} {url} returned HTTP {response.status}",
                status=response.status,
            )
        return response

    def get_json(self, url: str, **kwargs: Any) -> Any:
        """GET *url* and decode the response body as JSON."""
        response = self.request("GET", url, **kwargs)
        try:
            return response.json()
        except ValueError as exc:
            raise HTTPError(f"response from {url} is not valid JSON") from exc

    def close(self) -> None:
        """Close all pooled connections."""
        self._pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
