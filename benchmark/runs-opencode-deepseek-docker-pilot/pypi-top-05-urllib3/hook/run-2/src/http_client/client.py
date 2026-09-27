"""HTTP client with explicit control over connection pooling and retries.

The client is built on ``requests`` but reaches through its transport adapter to
``urllib3`` so the underlying connection pool size, blocking behaviour, and
retry/backoff policy can be configured directly.
"""

from __future__ import annotations

from typing import Iterable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_RETRY_STATUSES: tuple[int, ...] = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS: frozenset[str] = frozenset(
    {"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"}
)


def build_retry(
    total: int = 3,
    *,
    connect: Optional[int] = None,
    read: Optional[int] = None,
    status: Optional[int] = None,
    backoff_factor: float = 0.5,
    status_forcelist: Iterable[int] = DEFAULT_RETRY_STATUSES,
    allowed_methods: Iterable[str] = DEFAULT_RETRY_METHODS,
    respect_retry_after_header: bool = True,
    raise_on_status: bool = False,
) -> Retry:
    """Build a :class:`urllib3.util.retry.Retry` policy.

    ``total`` caps the number of retry attempts. The per-category limits
    (``connect``/``read``/``status``) default to ``total`` when left as ``None``.
    ``backoff_factor`` drives exponential backoff between attempts.
    """
    return Retry(
        total=total,
        connect=connect,
        read=read,
        status=status,
        backoff_factor=backoff_factor,
        status_forcelist=tuple(status_forcelist),
        allowed_methods=frozenset(allowed_methods),
        respect_retry_after_header=respect_retry_after_header,
        raise_on_status=raise_on_status,
    )


def build_session(
    *,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
    pool_block: bool = False,
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: Iterable[int] = DEFAULT_RETRY_STATUSES,
    allowed_methods: Iterable[str] = DEFAULT_RETRY_METHODS,
    user_agent: str = "http-client/0.1",
    verify: bool = True,
) -> requests.Session:
    """Return a ``requests.Session`` backed by a tuned pooled/retrying adapter.

    ``pool_connections`` is the number of distinct host pools kept alive and
    ``pool_maxsize`` the number of connections retained per pool. Setting
    ``pool_block=True`` makes callers wait for a free connection instead of
    discarding it and opening a new one.
    """
    retry = build_retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        pool_block=pool_block,
    )

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers["User-Agent"] = user_agent
    session.verify = verify
    return session


class HttpClient:
    """Small context-manager wrapper around a pooled, retrying session."""

    def __init__(self, **session_kwargs: object) -> None:
        self._session = build_session(**session_kwargs)  # type: ignore[arg-type]

    @property
    def session(self) -> requests.Session:
        return self._session

    def request(self, method: str, url: str, **kwargs: object) -> requests.Response:
        return self._session.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: object) -> requests.Response:
        return self._session.get(url, **kwargs)

    def post(self, url: str, **kwargs: object) -> requests.Response:
        return self._session.post(url, **kwargs)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
