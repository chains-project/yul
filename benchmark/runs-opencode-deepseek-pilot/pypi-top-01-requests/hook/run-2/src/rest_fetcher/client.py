"""HTTP client helpers for fetching data from a REST API."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests


class RestClient:
    """Thin wrapper around ``requests.Session`` for JSON REST APIs."""

    def __init__(
        self,
        base_url: str = "",
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(
        self,
        path: str = "",
        *,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Fetch a resource and return the decoded JSON body."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "RestClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def fetch_json(
    url: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = 30.0,
) -> Any:
    """Convenience function to GET ``url`` and return decoded JSON."""
    with RestClient(headers=headers, timeout=timeout) as client:
        return client.get(url, params=params)
