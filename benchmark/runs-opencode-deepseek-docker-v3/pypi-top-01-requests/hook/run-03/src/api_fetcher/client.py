"""HTTP client wrapper for talking to a JSON REST API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


class ApiError(RuntimeError):
    """Raised when a request fails or the API returns an error response."""


class RestClient:
    """Thin wrapper around :class:`httpx.Client` returning decoded JSON."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = 10.0,
        headers: Mapping[str, str] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=dict(headers) if headers else None,
        )

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """GET ``path`` and return the decoded JSON body."""
        return self._request("GET", path, params=params)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._client.request(method, path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(
                f"{method} {exc.request.url} returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise ApiError(f"{method} {exc.request.url} failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(
                f"{method} {response.request.url} did not return valid JSON"
            ) from exc

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> RestClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
