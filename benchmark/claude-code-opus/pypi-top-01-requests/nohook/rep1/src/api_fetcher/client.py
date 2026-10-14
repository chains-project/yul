"""Thin HTTP client wrapper for a REST API."""

from __future__ import annotations

from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3


class ApiError(RuntimeError):
    """Raised when the API returns an error or cannot be reached."""


class ApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            transport=transport or httpx.HTTPTransport(retries=retries),
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET `path` and return the decoded JSON body."""
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(
                f"{exc.response.status_code} from {exc.request.url}: {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"Request to {exc.request.url} failed: {exc}") from exc
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
