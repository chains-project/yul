"""HTTP helpers for fetching data from a REST API."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests

DEFAULT_TIMEOUT = 30.0


class ApiError(RuntimeError):
    """Raised when a request to the API fails."""


def fetch_json(
    url: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> Any:
    """Fetch and decode a JSON document from ``url`` over HTTP(S).

    Raises:
        ApiError: if the connection fails or the server returns an error status.
    """
    requester = session if session is not None else requests
    try:
        response = requester.get(
            url, params=params, headers=headers, timeout=timeout
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApiError(f"request to {url!r} failed: {exc}") from exc
    return response.json()
