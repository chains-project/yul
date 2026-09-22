"""Low-level HTTP client with connection pooling and automatic retries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import urllib3
from urllib3 import HTTPResponse, PoolManager, Retry, Timeout

_RetryableStatuses = Sequence[int]


class HttpClient:
    """A thin, explicit wrapper around :class:`urllib3.PoolManager`.

    It exposes connection pooling, configurable timeouts and automatic
    retries without hiding urllib3's low-level behaviour.
    """

    def __init__(
        self,
        *,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        pool_block: bool = False,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        retry_statuses: _RetryableStatuses | None = None,
        allowed_methods: Sequence[str] | None = None,
        timeout: float | Timeout | None = 10.0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self._retries = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            redirect=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=retry_statuses,
            allowed_methods=allowed_methods,
            raise_on_status=False,
        )
        if isinstance(timeout, (int, float)):
            timeout = Timeout(total=timeout)
        self._timeout = timeout
        self._pool = PoolManager(
            num_pools=pool_connections,
            maxsize=pool_maxsize,
            block=pool_block,
            retries=self._retries,
            timeout=self._timeout,
            headers=headers,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        fields: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | Timeout | None = None,
        retries: Retry | None = None,
        preload_content: bool = True,
        decode_content: bool = True,
    ) -> HTTPResponse:
        """Perform a request through the shared connection pool."""
        return self._pool.request(
            method,
            url,
            body=body,
            fields=fields,
            headers=headers,
            timeout=timeout,
            retries=retries,
            preload_content=preload_content,
            decode_content=decode_content,
        )

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Close all pooled connections."""
        self._pool.clear()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def build_default_client() -> HttpClient:
    """Return a client with sane defaults for general use."""
    return HttpClient(
        max_retries=3,
        backoff_factor=0.5,
        retry_statuses=(429, 500, 502, 503, 504),
    )


__all__ = ["HttpClient", "build_default_client", "urllib3"]
