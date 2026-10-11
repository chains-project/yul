from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any

import urllib3
from urllib3 import Retry
from urllib3.response import BaseHTTPResponse

logger = logging.getLogger(__name__)

DEFAULT_RETRY_STATUSES = frozenset({413, 429, 500, 502, 503, 504})
DEFAULT_RETRY_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"})

_UNSET: Any = object()


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    total: int = 3
    connect: int | None = None
    read: int | None = None
    backoff_factor: float = 0.5
    backoff_max: float = 30.0
    backoff_jitter: float = 0.0
    status_forcelist: frozenset[int] = DEFAULT_RETRY_STATUSES
    allowed_methods: frozenset[str] | None = DEFAULT_RETRY_METHODS
    respect_retry_after_header: bool = True
    raise_on_status: bool = False

    def build(self) -> Retry:
        return Retry(
            total=self.total,
            connect=self.connect,
            read=self.read,
            redirect=0,
            status=self.total,
            other=self.total,
            backoff_factor=self.backoff_factor,
            backoff_max=self.backoff_max,
            backoff_jitter=self.backoff_jitter,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
            respect_retry_after_header=self.respect_retry_after_header,
            raise_on_status=self.raise_on_status,
        )


@dataclass(frozen=True, slots=True)
class PoolConfig:
    num_pools: int = 10
    maxsize: int = 10
    block: bool = False
    timeout: float | None = 10.0
    retries: RetryPolicy = field(default_factory=RetryPolicy)


class HttpClient:
    def __init__(
        self,
        pool: PoolConfig | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        cert_reqs: str = "CERT_REQUIRED",
        ca_certs: str | None = None,
        **pool_options: Any,
    ) -> None:
        self.pool = pool or PoolConfig()
        self._manager = urllib3.PoolManager(
            num_pools=self.pool.num_pools,
            maxsize=self.pool.maxsize,
            block=self.pool.block,
            timeout=self.pool.timeout,
            retries=self.pool.retries.build(),
            headers=dict(headers) if headers else None,
            cert_reqs=cert_reqs,
            ca_certs=ca_certs,
            **pool_options,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        headers: Mapping[str, str] | None = None,
        retries: Retry | int | bool | None = None,
        timeout: float | urllib3.Timeout | tuple[float, float] | None | object = _UNSET,
        redirect: bool = True,
        **kwargs: Any,
    ) -> BaseHTTPResponse:
        if timeout is not _UNSET:
            kwargs["timeout"] = timeout
        return self._manager.request(
            method,
            url,
            body=body,
            headers=dict(headers) if headers else None,
            retries=retries,
            redirect=redirect,
            **kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> BaseHTTPResponse:
        return self.request("GET", url, **kwargs)

    def get_many(
        self,
        urls: Iterable[str],
        *,
        max_workers: int | None = None,
        **kwargs: Any,
    ) -> list[BaseHTTPResponse]:
        from concurrent.futures import ThreadPoolExecutor

        url_list = list(urls)
        workers = max_workers or min(32, len(url_list) or 1)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            return list(executor.map(lambda u: self.get(u, **kwargs), url_list))

    def close(self) -> None:
        self._manager.clear()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
