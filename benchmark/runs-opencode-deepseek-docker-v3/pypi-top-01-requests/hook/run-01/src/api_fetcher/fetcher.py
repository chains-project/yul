"""HTTP client helpers for fetching REST API resources."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


class ApiError(RuntimeError):
    """Raised when the API returns an error or an invalid response."""


def _resolve_url(path: str, base_url: str | None) -> str:
    if path.startswith(("http://", "https://")):
        return path

    base = base_url or os.environ.get("API_BASE_URL")
    if not base:
        raise ApiError(
            "No base URL given. Pass base_url or set the API_BASE_URL environment variable."
        )
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def fetch(
    path: str,
    *,
    base_url: str | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    token: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """Fetch `path` from a REST API and return the decoded JSON body.

    `path` may be an absolute URL or a path relative to `base_url`
    (or the `API_BASE_URL` environment variable).
    """
    url = _resolve_url(path, base_url)

    request_headers = dict(headers or {})
    api_token = token or os.environ.get("API_TOKEN")
    if api_token:
        request_headers.setdefault("Authorization", f"Bearer {api_token}")
    request_headers.setdefault("Accept", "application/json")

    try:
        response = httpx.get(
            url, params=params, headers=request_headers, timeout=timeout, follow_redirects=True
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ApiError(
            f"API returned {exc.response.status_code} for {exc.request.url}"
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(f"Request to {url} failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"Response from {url} was not valid JSON") from exc
