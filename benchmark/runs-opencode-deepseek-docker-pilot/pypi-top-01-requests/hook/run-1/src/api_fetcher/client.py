"""HTTP client for a REST API."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(RuntimeError):
    """Raised when an API request fails or returns an error status."""


class ApiClient:
    """Thin wrapper around :class:`requests.Session` for JSON REST APIs.

    ``base_url`` is optional when only absolute URLs are passed to :meth:`get`.
    """

    def __init__(
        self,
        base_url: str = "",
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        """GET ``path`` and return the decoded JSON body.

        ``path`` may be an absolute URL or a path relative to ``base_url``.
        """
        url = self._resolve(path)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ApiError(f"GET {url} failed: {exc}") from exc
        return response.json()

    def _resolve(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            raise ValueError(
                f"relative path {path!r} requires a base_url"
            )
        return f"{self.base_url}/{path.lstrip('/')}"

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
