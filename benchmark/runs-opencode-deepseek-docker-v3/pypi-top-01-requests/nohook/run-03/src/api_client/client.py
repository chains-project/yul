"""A small, reusable REST API client built on :mod:`httpx`."""

from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from api_client.config import DEFAULT_RETRIES, DEFAULT_TIMEOUT
from api_client.exceptions import APIError


class APIClient:
    """Synchronous client for fetching JSON from a REST API.

    Can be used as a context manager to ensure the underlying connection
    pool is closed::

        with APIClient("https://api.example.com") as client:
            data = client.get_json("/users", params={"page": 1})
    """

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=timeout,
            transport=httpx.HTTPTransport(retries=retries),
        )

    def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """GET ``path`` and return the decoded JSON body.

        Raises:
            APIError: if the request fails or the response is not successful.
        """
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise APIError(
                f"{exc.response.status_code} response from {exc.request.url}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise APIError(f"request failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise APIError("response body was not valid JSON") from exc

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
