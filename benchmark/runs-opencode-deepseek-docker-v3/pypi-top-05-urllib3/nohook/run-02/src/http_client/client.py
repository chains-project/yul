from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import urllib3
from urllib3.util import Retry, Timeout

DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset({"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"})


@dataclass(frozen=True)
class RetryPolicy:
    """Declarative description of automatic retry behaviour."""

    total: int = 3
    connect: int | None = None
    read: int | None = None
    status: int | None = None
    backoff_factor: float = 0.5
    status_forcelist: Sequence[int] = DEFAULT_RETRY_STATUSES
    allowed_methods: frozenset[str] = DEFAULT_RETRY_METHODS
    respect_retry_after_header: bool = True
    raise_on_status: bool = False

    def to_urllib3(self) -> Retry:
        return Retry(
            total=self.total,
            connect=self.connect,
            read=self.read,
            status=self.status,
            backoff_factor=self.backoff_factor,
            status_forcelist=list(self.status_forcelist),
            allowed_methods=set(self.allowed_methods),
            respect_retry_after_header=self.respect_retry_after_header,
            raise_on_status=self.raise_on_status,
        )


@dataclass(frozen=True)
class PoolConfig:
    """Tuning knobs for the underlying connection pools."""

    num_pools: int = 10
    maxsize: int = 10
    block: bool = False
    retries: RetryPolicy = field(default_factory=RetryPolicy)


class HttpClient:
    """Thin, reusable wrapper around :class:`urllib3.PoolManager`.

    Keeps a pool of keep-alive connections per host and transparently
    retries idempotent requests on connection, read and status failures.
    """

    def __init__(
        self,
        *,
        pool: PoolConfig | None = None,
        timeout: Timeout | float | None = 10.0,
        verify: bool = True,
        ca_certs: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.pool_config = pool or PoolConfig()
        self.timeout = timeout
        self.headers = dict(headers or {})
        self._manager = urllib3.PoolManager(
            num_pools=self.pool_config.num_pools,
            maxsize=self.pool_config.maxsize,
            block=self.pool_config.block,
            retries=self.pool_config.retries.to_urllib3(),
            timeout=timeout,
            cert_reqs="CERT_REQUIRED" if verify else "CERT_NONE",
            ca_certs=ca_certs,
            headers=self.headers,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        fields: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: Timeout | float | None = None,
        retries: Retry | None = None,
        redirect: bool = True,
    ) -> urllib3.response.HTTPResponse:
        return self._manager.request(
            method,
            url,
            body=body,
            fields=fields,
            headers=dict(headers) if headers else None,
            timeout=timeout if timeout is not None else self.timeout,
            retries=retries,
            redirect=redirect,
        )

    def get(self, url: str, **kwargs: Any) -> urllib3.response.HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> urllib3.response.HTTPResponse:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self._manager.clear()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
