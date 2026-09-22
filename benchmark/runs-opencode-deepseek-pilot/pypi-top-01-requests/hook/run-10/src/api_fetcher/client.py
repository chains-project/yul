"""A small HTTP client for talking to JSON REST APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 10.0
RETRY_STATUSES = (429, 500, 502, 503, 504)


class ApiError(RuntimeError):
    """Raised when a request to the API fails."""


class ApiClient:
    """Thin wrapper around :class:`requests.Session` for JSON APIs."""

    def __init__(
        self,
        base_url: str = "",
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Mapping[str, str] | None = None,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else self._build_session(retries)
        if headers:
            self.session.headers.update(headers)

    @staticmethod
    def _build_session(retries: int) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=RETRY_STATUSES,
            allowed_methods=frozenset({"GET"}),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        """GET ``path`` and return the decoded JSON body."""
        url = self._url(path)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ApiError(f"GET {url} failed: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"GET {url} returned invalid JSON") from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
