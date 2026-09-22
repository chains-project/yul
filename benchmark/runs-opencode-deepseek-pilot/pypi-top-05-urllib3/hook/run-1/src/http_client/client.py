"""A small HTTP client with connection pooling and automatic retries.

urllib3 is used directly (rather than a higher-level wrapper) so the caller
keeps low-level control over connection reuse, timeouts, and retry behavior.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

import urllib3
from urllib3 import PoolManager, Retry
from urllib3.response import HTTPResponse

logger = logging.getLogger(__name__)

DEFAULT_RETRY_STATUSES = (
    429,
    500,
    502,
    503,
    504,
)


def build_retries(
    total: int = 5,
    backoff_factor: float = 0.5,
    status_forcelist: Optional[tuple] = None,
    allowed_methods: Optional[frozenset] = None,
) -> Retry:
    """Create a Retry policy with exponential backoff.

    Retries are attempted for connection failures, redirects, and the given
    HTTP status codes. ``backoff_factor`` controls the exponential delay
    between attempts (0.5 -> 0.5s, 1s, 2s, 4s, ...).
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        redirect=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist or DEFAULT_RETRY_STATUSES,
        allowed_methods=allowed_methods or frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )


class HttpClient:
    """Pooled HTTP client.

    A single ``PoolManager`` is shared across requests so that connections to
    the same host are reused. ``maxsize`` sets how many connections are kept
    per host; ``block=True`` makes callers wait for a free connection instead
    of silently opening extra ones.
    """

    def __init__(
        self,
        retries: Optional[Retry] = None,
        maxsize: int = 10,
        block: bool = False,
        timeout: float = 10.0,
        cert_reqs: str = "CERT_REQUIRED",
    ) -> None:
        self.timeout = timeout
        self.pool = PoolManager(
            num_pools=10,
            maxsize=maxsize,
            block=block,
            retries=retries or build_retries(),
            cert_reqs=cert_reqs,
            headers={"User-Agent": "http-client/0.1.0"},
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        retries: Optional[Retry] = None,
        preload_content: bool = True,
    ) -> HTTPResponse:
        """Send a request, reusing a pooled connection when possible."""
        return self.pool.request(
            method,
            url,
            body=body,
            headers=dict(headers) if headers else None,
            timeout=urllib3.Timeout(total=timeout if timeout is not None else self.timeout),
            retries=retries,
            preload_content=preload_content,
        )

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def close(self) -> None:
        self.pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with HttpClient() as client:
        resp = client.get("https://httpbin.org/get")
        print(f"{resp.status} {resp.headers.get('content-type')}")
        print(resp.data[:200])


if __name__ == "__main__":
    main()
