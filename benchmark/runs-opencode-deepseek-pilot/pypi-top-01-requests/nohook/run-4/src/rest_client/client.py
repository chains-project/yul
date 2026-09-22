"""HTTP client for fetching data from a REST API."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when a REST API request fails."""


class RestClient:
    """Thin wrapper around :mod:`requests` for talking to a REST API.

    Parameters
    ----------
    base_url:
        Root URL of the API, e.g. ``"https://api.example.com"``. Any trailing
        slash is removed so that relative paths join cleanly.
    timeout:
        Default timeout (seconds) applied to every request.
    headers:
        Default headers sent with every request.
    session:
        Optional pre-configured :class:`requests.Session` to reuse.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Mapping[str, str]] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url must not be empty")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(dict(headers))

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """GET ``path`` and return the decoded JSON body.

        Raises
        ------
        ApiError
            If the server returns a non-2xx status or the body is not JSON.
        """
        url = self._url(path)
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout if timeout is None else timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ApiError(f"GET {url} failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"GET {url} returned a non-JSON response") from exc

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> "RestClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
