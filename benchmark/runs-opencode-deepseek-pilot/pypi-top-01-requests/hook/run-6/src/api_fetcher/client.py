"""HTTP client for talking to a REST API."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests


class ApiError(Exception):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """Thin wrapper around :mod:`requests` for a JSON REST API."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        headers: Optional[Mapping[str, str]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if headers:
            self.session.headers.update(headers)

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        """GET ``path`` and return the decoded JSON body."""
        url = path if path.startswith(("http://", "https://")) else f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiError(f"request to {url} failed: {exc}") from exc

        if not response.ok:
            raise ApiError(
                f"GET {url} returned {response.status_code}",
                status_code=response.status_code,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"response from {url} was not valid JSON") from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
