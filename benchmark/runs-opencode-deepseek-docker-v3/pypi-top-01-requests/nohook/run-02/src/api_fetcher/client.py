"""HTTP client helpers for talking to a REST API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when the API request fails or returns an error status."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(slots=True)
class ApiResponse:
    """A parsed JSON response from the API."""

    status_code: int
    data: Any
    headers: dict[str, str] = field(default_factory=dict)


def fetch(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    json: Any | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    client: httpx.Client | None = None,
) -> ApiResponse:
    """Fetch a URL and return the decoded JSON body.

    Raises:
        ApiError: if the request fails or the server returns a non-2xx status.
    """
    own_client = client is None
    client = client or httpx.Client(timeout=timeout)
    try:
        response = client.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError as exc:
            raise ApiError("Response body is not valid JSON", response.status_code) from exc
        return ApiResponse(
            status_code=response.status_code,
            data=data,
            headers=dict(response.headers),
        )
    except httpx.HTTPStatusError as exc:
        raise ApiError(
            f"HTTP {exc.response.status_code} for {exc.request.url}",
            exc.response.status_code,
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(f"Request to {url} failed: {exc}") from exc
    finally:
        if own_client:
            client.close()
