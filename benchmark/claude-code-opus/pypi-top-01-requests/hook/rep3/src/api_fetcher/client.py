"""Thin HTTP client wrapper for a REST API."""

from typing import Any, Self

import httpx

DEFAULT_TIMEOUT = 10.0


class ApiClient:
    def __init__(
        self,
        base_url: str,
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
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET `path` and return the decoded JSON body. Raises httpx.HTTPStatusError on 4xx/5xx."""
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
