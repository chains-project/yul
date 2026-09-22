"""Connection-pooled HTTP client with automatic retries."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import urllib3
from urllib3.util import Timeout
from urllib3.util.retry import Retry

from http_client.retries import DEFAULT_RETRIES


class HttpClient:
    """Thin wrapper around ``urllib3.PoolManager``.

    Gives the caller low-level control over connection pooling, timeouts,
    TLS verification and retry behaviour while keeping a single reusable
    pool for the lifetime of the instance.
    """

    def __init__(
        self,
        *,
        num_pools: int = 10,
        maxsize: int = 10,
        block: bool = False,
        retries: Optional[Retry] = None,
        connect_timeout: Optional[float] = 5.0,
        read_timeout: Optional[float] = 30.0,
        cert_reqs: str = "CERT_REQUIRED",
        ca_certs: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.retries = retries if retries is not None else DEFAULT_RETRIES
        self._pool = urllib3.PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=self.retries,
            timeout=Timeout(connect=connect_timeout, read=read_timeout),
            cert_reqs=cert_reqs,
            ca_certs=ca_certs,
            headers=dict(headers) if headers else None,
        )

    def request(self, method: str, url: str, **kwargs: Any) -> urllib3.response.HTTPResponse:
        """Issue a request, reusing pooled connections and retrying on failure."""
        return self._pool.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> urllib3.response.HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> urllib3.response.HTTPResponse:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        """Close all pooled connections."""
        self._pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
