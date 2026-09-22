"""HTTP client helpers for fetching data from REST APIs."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def build_session(
    retries: int = DEFAULT_RETRIES,
    backoff_factor: float = 0.5,
) -> requests.Session:
    """Create a ``requests.Session`` with automatic retries on transient errors."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods=frozenset({"GET", "HEAD"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch(
    url: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> requests.Response:
    """Perform a GET request and return the response.

    Raises ``requests.HTTPError`` for non-successful status codes and
    ``requests.RequestException`` for connection-level failures.
    """
    owns_session = session is None
    session = session or build_session()
    try:
        response = session.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    finally:
        if owns_session:
            session.close()


def fetch_json(
    url: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> Any:
    """Fetch ``url`` and decode the response body as JSON."""
    return fetch(
        url,
        params=params,
        headers=headers,
        timeout=timeout,
        session=session,
    ).json()
