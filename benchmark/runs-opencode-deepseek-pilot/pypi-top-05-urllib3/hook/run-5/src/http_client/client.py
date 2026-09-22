from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

import urllib3
from urllib3 import PoolManager
from urllib3.util.retry import Retry

DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset(
    ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
)


def build_retries(
    total: int = 5,
    backoff_factor: float = 0.5,
    status_forcelist: Sequence[int] = DEFAULT_RETRY_STATUSES,
    allowed_methods: Optional[Sequence[str]] = DEFAULT_RETRY_METHODS,
    respect_retry_after_header: bool = True,
) -> Retry:
    """Build a Retry policy with exponential backoff."""
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        respect_retry_after_header=respect_retry_after_header,
        raise_on_status=False,
    )


def build_pool_manager(
    retries: Optional[Retry] = None,
    num_pools: int = 10,
    maxsize: int = 10,
    block: bool = False,
    timeout: Any = None,
    cert_reqs: str = "CERT_REQUIRED",
    **kwargs: Any,
) -> PoolManager:
    """Build a PoolManager that reuses connections across requests.

    ``maxsize`` caps the connections kept per host; ``block=True`` makes
    callers wait for a free connection instead of opening a new one.
    """
    if retries is None:
        retries = build_retries()
    return PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retries,
        timeout=timeout,
        cert_reqs=cert_reqs,
        **kwargs,
    )


class HttpClient:
    """Thin wrapper around urllib3's PoolManager."""

    def __init__(
        self,
        base_url: str = "",
        retries: Optional[Retry] = None,
        timeout: Any = None,
        **pool_kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._pool = build_pool_manager(retries=retries, timeout=timeout, **pool_kwargs)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        body: Any = None,
        fields: Optional[Mapping[str, Any]] = None,
        timeout: Any = None,
        retries: Optional[Retry] = None,
        **kwargs: Any,
    ) -> urllib3.HTTPResponse:
        target = url if "://" in url else f"{self.base_url}{url}"
        return self._pool.request(
            method,
            target,
            headers=headers,
            body=body,
            fields=fields,
            timeout=timeout if timeout is not None else self.timeout,
            retries=retries,
            **kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> urllib3.HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> urllib3.HTTPResponse:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self._pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
