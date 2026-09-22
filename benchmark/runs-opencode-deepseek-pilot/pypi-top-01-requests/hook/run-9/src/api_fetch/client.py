"""HTTP client for talking to a REST API."""

from typing import Any, Dict, Optional

import requests


class ApiError(Exception):
    """Raised when the API returns an error response."""


class ApiClient:
    """Thin wrapper around :mod:`requests` for a JSON REST API."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _url(self, path: str) -> str:
        return "{}/{}".format(self.base_url, path.lstrip("/"))

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET *path* and return the decoded JSON body."""
        try:
            response = self.session.get(
                self._url(path), params=params, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise ApiError("request to {} failed: {}".format(path, exc)) from exc

        if not response.ok:
            raise ApiError(
                "{} returned HTTP {}".format(path, response.status_code)
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError("{} did not return valid JSON".format(path)) from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()
