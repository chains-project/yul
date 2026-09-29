from __future__ import annotations

from typing import Iterable, Optional

from urllib3 import PoolManager, Retry, Timeout
from urllib3.response import HTTPResponse

DEFAULT_STATUS_FORCELIST: tuple[int, ...] = (413, 429, 500, 502, 503, 504)

IDEMPOTENT_METHODS: frozenset[str] = frozenset(
    {"DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE"}
)


def build_retry(
    total: int = 5,
    *,
    backoff_factor: float = 0.5,
    backoff_max: float = 60.0,
    status_forcelist: Iterable[int] = DEFAULT_STATUS_FORCELIST,
    allowed_methods: Iterable[str] = IDEMPOTENT_METHODS,
) -> Retry:
    """Build a retry policy shared by every connection in the pool.

    ``total`` bounds connect/read/redirect/status retries individually.
    ``allowed_methods`` defaults to idempotent verbs only; add ``"POST"``
    explicitly if the caller has arranged for safe replay.
    """
    return Retry(
        total=total,
        connect=total,
        read=total,
        redirect=total,
        status=total,
        other=total,
        backoff_factor=backoff_factor,
        backoff_max=backoff_max,
        status_forcelist=tuple(status_forcelist),
        allowed_methods=frozenset(method.upper() for method in allowed_methods),
        respect_retry_after_header=True,
        raise_on_status=False,
    )


class HttpClient:
    """A small wrapper over :class:`urllib3.PoolManager`.

    The pool manager owns connection reuse across hosts; ``max_connections``
    caps sockets per host pool and ``block`` decides whether a saturated pool
    waits or fails fast.
    """

    def __init__(
        self,
        *,
        num_pools: int = 10,
        max_connections: int = 10,
        block: bool = False,
        retries: Optional[Retry] = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        **pool_kwargs: object,
    ) -> None:
        self.retries = retries if retries is not None else build_retry()
        self.timeout = Timeout(connect=connect_timeout, read=read_timeout)
        self.pool = PoolManager(
            num_pools=num_pools,
            maxsize=max_connections,
            block=block,
            retries=self.retries,
            timeout=self.timeout,
            **pool_kwargs,
        )

    def request(self, method: str, url: str, **kwargs: object) -> HTTPResponse:
        return self.pool.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: object) -> HTTPResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, body: object = None, **kwargs: object) -> HTTPResponse:
        return self.request("POST", url, body=body, **kwargs)

    def close(self) -> None:
        self.pool.clear()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
