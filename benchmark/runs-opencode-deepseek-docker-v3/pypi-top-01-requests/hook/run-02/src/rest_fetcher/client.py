from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0
DEFAULT_USER_AGENT = "rest-fetcher/0.1"


class ApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._owns_client = client is None
        default_headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}
        if headers:
            default_headers.update(headers)
        self._client = client or httpx.Client(
            base_url=self.base_url,
            headers=default_headers,
            timeout=timeout,
            follow_redirects=True,
        )

    def get(self, path: str, **params: Any) -> Any:
        return self._request("GET", path, params=params or None)

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(
                f"{exc.request.method} {exc.request.url} failed with {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"request to {path!r} failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"response from {path!r} was not valid JSON") from exc

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


def fetch_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(
                f"GET {exc.request.url} failed with {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"request to {url!r} failed: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"response from {url!r} was not valid JSON") from exc
