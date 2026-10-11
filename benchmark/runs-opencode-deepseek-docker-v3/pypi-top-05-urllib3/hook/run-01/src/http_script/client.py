from __future__ import annotations

from collections.abc import Collection, Mapping
from types import TracebackType
from typing import Any

from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import HTTPResponse

DEFAULT_STATUS_FORCELIST = (429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS: frozenset[str] = frozenset(
    {"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"}
)


def build_retry(
    *,
    total: int = 5,
    connect: int | None = None,
    read: int | None = None,
    redirect: int = 0,
    status: int | None = None,
    backoff_factor: float = 0.5,
    status_forcelist: Collection[int] = DEFAULT_STATUS_FORCELIST,
    allowed_methods: Collection[str] | None = DEFAULT_ALLOWED_METHODS,
    respect_retry_after_header: bool = True,
    raise_on_status: bool = False,
) -> Retry:
    total = max(total, 0)
    return Retry(
        total=total,
        connect=total if connect is None else connect,
        read=total if read is None else read,
        redirect=redirect,
        status=total if status is None else status,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        respect_retry_after_header=respect_retry_after_header,
        raise_on_status=raise_on_status,
    )


class HttpClient:
    def __init__(
        self,
        *,
        num_pools: int = 10,
        maxsize: int = 10,
        block: bool = False,
        timeout: float | Timeout | None = 10.0,
        retries: Retry | int | None = None,
        headers: Mapping[str, str] | None = None,
        **pool_kwargs: Any,
    ) -> None:
        if retries is None:
            retries = build_retry()
        elif isinstance(retries, int):
            retries = build_retry(total=retries)
        self._retries = retries
        self._pool = PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            timeout=timeout,
            retries=retries,
            headers=headers,
            **pool_kwargs,
        )

    @property
    def retries(self) -> Retry:
        return self._retries

    def request(
        self,
        method: str,
        url: str,
        *,
        fields: Mapping[str, Any] | None = None,
        body: Any = None,
        headers: Mapping[str, str] | None = None,
        json: Any = None,
        preload_content: bool = True,
        **kwargs: Any,
    ) -> HTTPResponse:
        return self._pool.request(
            method,
            url,
            fields=fields,
            body=body,
            headers=headers,
            json=json,
            preload_content=preload_content,
            **kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        self._pool.clear()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
