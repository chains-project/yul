from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import urllib3
from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import BaseHTTPResponse

DEFAULT_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
DEFAULT_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE", "TRACE"})


@dataclass(frozen=True)
class RetryConfig:
    total: int = 3
    connect: int | None = None
    read: int | None = None
    status: int | None = None
    backoff_factor: float = 0.5
    backoff_max: float = 30.0
    status_forcelist: frozenset[int] = field(default_factory=lambda: DEFAULT_RETRY_STATUSES)
    allowed_methods: frozenset[str] = field(default_factory=lambda: DEFAULT_RETRY_METHODS)
    respect_retry_after_header: bool = True
    raise_on_status: bool = False

    def build(self) -> Retry:
        return Retry(
            total=self.total,
            connect=self.connect,
            read=self.read,
            status=self.status,
            backoff_factor=self.backoff_factor,
            backoff_max=self.backoff_max,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
            respect_retry_after_header=self.respect_retry_after_header,
            raise_on_status=self.raise_on_status,
        )


@dataclass(frozen=True)
class TimeoutConfig:
    connect: float | None = 5.0
    read: float | None = 30.0

    def build(self) -> Timeout:
        return Timeout(connect=self.connect, read=self.read)


class PooledHTTPClient:
    def __init__(
        self,
        *,
        num_pools: int = 10,
        maxsize: int = 10,
        block: bool = False,
        retries: RetryConfig | None = None,
        timeout: TimeoutConfig | None = None,
        headers: Mapping[str, str] | None = None,
        cert_reqs: str = "CERT_REQUIRED",
        ca_certs: str | None = None,
        pool_manager: PoolManager | None = None,
    ) -> None:
        self.headers = dict(headers or {})
        self._retries = (retries or RetryConfig())
        self._pool = pool_manager or PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=self._retries.build(),
            timeout=(timeout or TimeoutConfig()).build(),
            cert_reqs=cert_reqs,
            ca_certs=ca_certs,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        fields: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
        body: bytes | str | None = None,
        headers: Mapping[str, str] | None = None,
        retries: RetryConfig | Retry | None = None,
        timeout: TimeoutConfig | Timeout | None = None,
        redirect: bool = True,
        preload_content: bool = True,
        decode_content: bool = True,
        **kwargs: Any,
    ) -> BaseHTTPResponse:
        merged_headers = {**self.headers, **(headers or {})}
        retry_arg = self._resolve_retries(retries)
        timeout_arg = self._resolve_timeout(timeout)
        return self._pool.request(
            method,
            url,
            body=body,
            fields=fields,
            headers=merged_headers,
            retries=retry_arg,
            timeout=timeout_arg,
            redirect=redirect,
            preload_content=preload_content,
            decode_content=decode_content,
            **kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> BaseHTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> BaseHTTPResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> BaseHTTPResponse:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> BaseHTTPResponse:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        self._pool.clear()

    def __enter__(self) -> PooledHTTPClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _resolve_retries(self, retries: RetryConfig | Retry | None) -> Retry | None:
        if retries is None:
            return None
        if isinstance(retries, RetryConfig):
            return retries.build()
        return retries

    def _resolve_timeout(self, timeout: TimeoutConfig | Timeout | None) -> Timeout | None:
        if timeout is None:
            return None
        if isinstance(timeout, TimeoutConfig):
            return timeout.build()
        return timeout


def default_client(**kwargs: Any) -> PooledHTTPClient:
    return PooledHTTPClient(**kwargs)


__all__ = ["PooledHTTPClient", "RetryConfig", "TimeoutConfig", "default_client", "urllib3"]
