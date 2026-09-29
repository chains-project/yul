"""HTTP client for a JSON REST API."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(Exception):
    """Raised when a request fails or the API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """Thin wrapper around :mod:`requests` for a JSON REST API."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers["Accept"] = "application/json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Fetch a resource and return the decoded JSON body."""
        return self.request("GET", path, params=params)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ApiError(f"{method} {url} failed: {exc}") from exc

        if not response.ok:
            raise ApiError(
                f"{method} {url} returned {response.status_code}",
                status_code=response.status_code,
            )

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"{method} {url} did not return valid JSON") from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
