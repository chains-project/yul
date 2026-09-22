"""HTTP client helpers for fetching JSON from a REST API."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when a request to the REST API fails."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    session: Optional[requests.Session] = None,
) -> Any:
    """Fetch and decode a JSON response from ``url``.

    Args:
        url: The endpoint to request.
        method: HTTP method to use.
        params: Optional query string parameters.
        headers: Optional request headers.
        timeout: Request timeout in seconds.
        session: Optional pre-configured ``requests.Session``.

    Returns:
        The decoded JSON body.

    Raises:
        ApiError: If the request fails, times out, or returns a non-2xx
            status or a body that is not valid JSON.
    """
    requester = session or requests
    try:
        response = requester.request(
            method,
            url,
            params=params,
            headers=headers,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ApiError(f"Request to {url} failed: {exc}") from exc

    if not response.ok:
        raise ApiError(
            f"Request to {url} returned {response.status_code}",
            status_code=response.status_code,
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"Response from {url} was not valid JSON") from exc
