"""Thin HTTP client wrapper for a REST API."""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0


class ApiError(Exception):
    """Raised when the API request fails or returns an error status."""


class ApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            transport=transport,
            follow_redirects=True,
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET `path` and return the decoded JSON body."""
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(f"{exc.response.status_code} error from {exc.request.url}") from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"request to {exc.request.url} failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"response from {response.url} is not valid JSON") from exc

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
