"""HTTP client helpers for talking to a JSON REST API."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3


class ApiError(Exception):
    """Raised when a request fails or the server returns an error status."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _build_session(retries: int = DEFAULT_RETRIES) -> requests.Session:
    """Create a session that retries transient failures with backoff."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class RestClient:
    """A thin wrapper around :class:`requests.Session` for JSON APIs."""

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or _build_session(retries)
        self.session.headers.update({"Accept": "application/json"})
        if headers:
            self.session.headers.update(dict(headers))

    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            return path
        return "{}/{}".format(self.base_url, path.lstrip("/"))

    def get(
        self,
        path: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """GET ``path`` and return the decoded JSON body."""
        url = self._url(path)
        try:
            response = self.session.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise ApiError("request to {} failed: {}".format(url, exc)) from exc

        if not response.ok:
            raise ApiError(
                "{} returned HTTP {}".format(url, response.status_code),
                status_code=response.status_code,
            )

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError("{} did not return valid JSON".format(url)) from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "RestClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def fetch(
    url: str,
    params: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """One-shot helper: GET ``url`` and return the decoded JSON body."""
    with RestClient(timeout=timeout) as client:
        return client.get(url, params=params, headers=headers)
