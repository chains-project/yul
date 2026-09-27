from __future__ import annotations

from typing import Any

import requests


class ApiError(RuntimeError):
    """Raised when the API returns an error response."""


class ApiClient:
    """Thin wrapper around a JSON REST API."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ApiError(
                f"{response.status_code} {response.reason} for {response.url}"
            ) from exc
        return response.json()
