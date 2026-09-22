"""Minimal HTTP client for fetching JSON from a REST API."""

from __future__ import annotations

from typing import Any, Mapping

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when a request to the API fails."""


def fetch_json(
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """Fetch ``url`` and return the decoded JSON body.

    Raises :class:`ApiError` on a non-2xx response or a network failure.
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise ApiError(f"HTTP {exc.response.status_code} for {exc.request.url}") from exc
    except requests.RequestException as exc:
        raise ApiError(f"request to {url} failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"response from {url} was not valid JSON") from exc
