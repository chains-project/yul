"""HTTP client for fetching data from a REST API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import requests


class ApiError(RuntimeError):
    """Raised when the API returns an unsuccessful response."""


class ApiClient:
    """Minimal REST API client built on top of :mod:`requests`."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        headers: Mapping[str, str] | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Fetch *path* relative to ``base_url`` and return the parsed JSON body."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        if not response.ok:
            raise ApiError(f"GET {url} failed with {response.status_code}: {response.text}")
        return response.json()
