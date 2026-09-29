from __future__ import annotations

from typing import Any, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(
        self,
        base_url: str = "",
        *,
        timeout: float = 10.0,
        retries: int = 3,
        headers: Optional[Mapping[str, str]] = None,
        session: Optional[requests.Session] = None,
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
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _resolve_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            raise ApiError(f"relative path {path!r} requires a base_url")
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> requests.Response:
        url = self._resolve_url(path)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise ApiError(f"GET {url} failed with status {status}") from exc
        except requests.RequestException as exc:
            raise ApiError(f"GET {url} failed: {exc}") from exc
        return response

    def get_json(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Any:
        try:
            return self.get(path, params=params).json()
        except ValueError as exc:
            raise ApiError(f"GET {self._resolve_url(path)} did not return valid JSON") from exc

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
