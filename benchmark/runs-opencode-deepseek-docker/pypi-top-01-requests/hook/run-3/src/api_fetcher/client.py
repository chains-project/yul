"""A small, dependency-light wrapper around a REST API over HTTP."""

from __future__ import annotations

from typing import Any, Mapping

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when a request cannot be completed or returns an error."""


class ApiClient:
    """Fetch JSON from a REST API using a reusable HTTP session.

    Example:
        with ApiClient("https://api.example.com", headers={"X-Api-Key": key}) as api:
            users = api.get("users", params={"limit": 10})
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session if session is not None else requests.Session()
        if headers:
            self._session.headers.update(headers)

    def get(
        self,
        path: str = "",
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """GET ``path`` relative to the base URL and return the decoded JSON."""
        if path:
            url = f"{self.base_url}/{path.lstrip('/')}"
        else:
            url = self.base_url

        try:
            response = self._session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiError(f"Request to {url} failed: {exc}") from exc

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ApiError(
                f"{url} returned HTTP {response.status_code}"
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"{url} did not return valid JSON") from exc

    def close(self) -> None:
        """Release the underlying connection pool."""
        self._session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
