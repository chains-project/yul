from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import HTTPResponse

RetryLike = Union[Retry, int]
TimeoutLike = Union[Timeout, float, int]

DEFAULT_RETRIES = Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    redirect=None,
    backoff_factor=0.5,
    backoff_max=30.0,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}),
    raise_on_status=False,
    respect_retry_after_header=True,
)

DEFAULT_TIMEOUT = Timeout(connect=5.0, read=30.0)


def _as_retry(value: Optional[RetryLike]) -> Optional[Retry]:
    if value is None or isinstance(value, Retry):
        return value
    return Retry.from_int(value)


def _as_timeout(value: Optional[TimeoutLike]) -> Optional[Timeout]:
    if value is None or isinstance(value, Timeout):
        return value
    return Timeout(total=float(value))


class HTTPClient:
    """Connection-pooled HTTP client with configurable automatic retries."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        *,
        retries: Optional[RetryLike] = None,
        timeout: Optional[TimeoutLike] = DEFAULT_TIMEOUT,
        maxsize: int = 10,
        block: bool = False,
        num_pools: int = 10,
        headers: Optional[Mapping[str, str]] = None,
        **pool_kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self._headers = dict(headers or {})
        self._retries = _as_retry(retries)
        self._timeout = _as_timeout(timeout)
        self._pool = PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=self._retries if self._retries is not None else DEFAULT_RETRIES,
            timeout=self._timeout if self._timeout is not None else DEFAULT_TIMEOUT,
            headers=self._headers,
            **pool_kwargs,
        )

    def _resolve(self, url: str) -> str:
        if self.base_url and not url.lower().startswith(("http://", "https://")):
            return f"{self.base_url}/{url.lstrip('/')}"
        return url

    def request(
        self,
        method: str,
        url: str,
        *,
        retries: Optional[RetryLike] = None,
        timeout: Optional[TimeoutLike] = None,
        **kwargs: Any,
    ) -> HTTPResponse:
        return self._pool.request(
            method,
            self._resolve(url),
            retries=_as_retry(retries),
            timeout=_as_timeout(timeout),
            headers={**self._headers, **kwargs.pop("headers", {})},
            **kwargs,
        )

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("OPTIONS", url, **kwargs)

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

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
