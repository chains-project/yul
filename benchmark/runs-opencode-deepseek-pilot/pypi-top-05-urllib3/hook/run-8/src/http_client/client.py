"""Low-level HTTP client built on urllib3.

Exposes explicit control over connection pooling, timeouts and retry
behaviour while keeping a small, script-friendly API.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional

import urllib3
from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import HTTPResponse


@dataclass
class HttpClient:
    """Thin wrapper around a urllib3 ``PoolManager``.

    The ``PoolManager`` keeps a pool of reusable connections per host, so
    repeated requests avoid the TCP/TLS handshake cost. ``Retry`` handles
    transient failures (connection resets, 429/5xx) with backoff.
    """

    pool: PoolManager
    timeout: Timeout

    def request(
        self,
        method: str,
        url: str,
        *,
        body: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        fields: Optional[Mapping[str, Any]] = None,
        retries: Optional[Retry] = None,
        redirect: bool = True,
        timeout: Optional[Timeout] = None,
    ) -> HTTPResponse:
        return self.pool.request(
            method,
            url,
            body=body,
            headers=dict(headers) if headers else None,
            fields=fields,
            retries=retries,
            redirect=redirect,
            timeout=timeout or self.timeout,
        )

    def get(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HTTPResponse:
        return self.request("POST", url, **kwargs)

    def close(self) -> None:
        self.pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def build_client(
    *,
    max_connections: int = 10,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
    allowed_methods: tuple[str, ...] = ("GET", "HEAD", "PUT", "DELETE", "OPTIONS", "POST"),
    connect_timeout: float = 5.0,
    read_timeout: float = 30.0,
    cert_reqs: str = "CERT_REQUIRED",
) -> HttpClient:
    """Create an :class:`HttpClient` with pooling and retries configured."""

    retries = Retry(
        total=max_retries,
        connect=max_retries,
        read=max_retries,
        status=max_retries,
        redirect=5,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(allowed_methods),
        raise_on_status=False,
        respect_retry_after_header=True,
    )

    pool = PoolManager(
        num_pools=max_connections,
        maxsize=max_connections,
        block=False,
        retries=retries,
        cert_reqs=cert_reqs,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
    )

    return HttpClient(
        pool=pool,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL with pooling and retries.")
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-d", "--data", default=None, help="Request body")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    client = build_client(max_retries=args.retries, read_timeout=args.timeout)
    try:
        response = client.request(args.method, args.url, body=args.data)
        print(
            json.dumps(
                {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": response.data.decode("utf-8", "replace"),
                },
                indent=2,
            )
        )
        return 0 if response.status < 400 else 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
