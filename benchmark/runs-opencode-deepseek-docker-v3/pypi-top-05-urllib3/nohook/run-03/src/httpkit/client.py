"""Low-level HTTP client built on urllib3.

Provides centralised control over connection pooling, timeouts and automatic
retries while still exposing the raw :class:`urllib3.response.HTTPResponse`.
"""

from __future__ import annotations

import json as _json
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, Optional, Sequence, Union

import certifi
import urllib3
from urllib3 import Retry, Timeout
from urllib3._collections import HTTPHeaderDict
from urllib3.poolmanager import PoolManager, ProxyManager
from urllib3.response import HTTPResponse

__all__ = ["RetryPolicy", "HTTPClient", "HTTPError"]

DEFAULT_RETRY_STATUSES = (413, 429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS = frozenset(
    {"DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE", "POST"}
)


class HTTPError(urllib3.exceptions.HTTPError):
    """Raised when a request ultimately fails after exhausting retries."""


@dataclass(frozen=True)
class RetryPolicy:
    """Declarative description of how requests should be retried.

    Mirrors :class:`urllib3.util.retry.Retry`, but keeps the knobs we care
    about in one place and gives safe defaults for idempotent + POST traffic.
    """

    total: int = 3
    connect: Optional[int] = None
    read: Optional[int] = None
    redirect: Optional[int] = None
    status: Optional[int] = None
    backoff_factor: float = 0.5
    backoff_max: float = 120.0
    status_forcelist: Sequence[int] = field(default=DEFAULT_RETRY_STATUSES)
    allowed_methods: Optional[Sequence[str]] = field(
        default_factory=lambda: DEFAULT_ALLOWED_METHODS
    )
    respect_retry_after_header: bool = True
    raise_on_status: bool = False

    def build(self) -> Retry:
        return Retry(
            total=self.total,
            connect=self.connect,
            read=self.read,
            redirect=self.redirect,
            status=self.status,
            backoff_factor=self.backoff_factor,
            backoff_max=self.backoff_max,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
            respect_retry_after_header=self.respect_retry_after_header,
            raise_on_status=self.raise_on_status,
        )


class HTTPClient:
    """A thin, explicit wrapper around :class:`urllib3.PoolManager`.

    Example:
        with HTTPClient(maxsize=20, retries=RetryPolicy(total=5)) as client:
            response = client.get("https://example.com/api")
            print(response.status)
    """

    def __init__(
        self,
        *,
        timeout: Union[float, Timeout] = 30.0,
        retries: Union[int, RetryPolicy, Retry, None] = None,
        maxsize: int = 10,
        num_pools: int = 10,
        block: bool = False,
        cert_reqs: str = "CERT_REQUIRED",
        ca_certs: Optional[str] = None,
        proxy_url: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
        **pool_kwargs: Any,
    ) -> None:
        self.timeout = timeout if isinstance(timeout, Timeout) else Timeout(total=timeout)
        self.retries = self._coerce_retries(retries)
        self.default_headers = dict(headers or {})
        self._pool_kwargs = pool_kwargs

        manager_cls = ProxyManager if proxy_url else PoolManager
        manager_kwargs: dict[str, Any] = {
            "maxsize": maxsize,
            "num_pools": num_pools,
            "block": block,
            "retries": self.retries,
            "timeout": self.timeout,
            "cert_reqs": cert_reqs,
            "ca_certs": ca_certs or certifi.where(),
            **pool_kwargs,
        }
        if proxy_url:
            manager_kwargs["proxy_url"] = proxy_url
        self.pool = manager_cls(**manager_kwargs)

    @staticmethod
    def _coerce_retries(
        retries: Union[int, RetryPolicy, Retry, None]
    ) -> Retry:
        if retries is None:
            return RetryPolicy().build()
        if isinstance(retries, Retry):
            return retries
        if isinstance(retries, RetryPolicy):
            return retries.build()
        if isinstance(retries, int):
            return RetryPolicy(total=retries).build()
        raise TypeError(f"Unsupported retries value: {retries!r}")

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        fields: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        redirect: bool = True,
        preload_content: bool = False,
        decode_content: bool = True,
        retries: Optional[Retry] = None,
        **urlopen_kwargs: Any,
    ) -> HTTPResponse:
        """Issue a request and return the live :class:`HTTPResponse`.

        ``preload_content`` defaults to ``False`` so callers retain low-level
        control over streaming and connection reuse. Set it to ``True`` for a
        fully buffered response.
        """
        merged_headers = HTTPHeaderDict(self.default_headers)
        merged_headers.update(headers or {})

        try:
            return self.pool.request(
                method,
                url,
                body=body,
                fields=fields,
                headers=merged_headers,
                redirect=redirect,
                preload_content=preload_content,
                decode_content=decode_content,
                retries=retries,
                **urlopen_kwargs,
            )
        except urllib3.exceptions.HTTPError as exc:
            raise HTTPError(f"{method} {url} failed: {exc}") from exc

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("DELETE", url, **kwargs)

    def stream(
        self,
        method: str,
        url: str,
        *,
        chunk_size: int = 8192,
        **kwargs: Any,
    ) -> Iterator[bytes]:
        """Yield decoded chunks, always releasing the connection afterwards."""
        kwargs.setdefault("preload_content", False)
        response = self.request(method, url, **kwargs)
        try:
            yield from response.stream(chunk_size, decode_content=True)
        finally:
            response.release_conn()

    def get_json(self, url: str, **kwargs: Any) -> Any:
        kwargs["preload_content"] = True
        response = self.request("GET", url, **kwargs)
        return _json.loads(response.data)

    def close(self) -> None:
        self.pool.clear()

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
