from __future__ import annotations

from typing import Any

import httpx

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3


class ApiError(Exception):
    """Raised when a request to the API fails."""


def fetch_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    transport: httpx.BaseTransport | None = None,
) -> Any:
    """Fetch and decode a JSON document from ``url``.

    Retries transient (5xx / connection) failures up to ``retries`` times and
    raises :class:`ApiError` once the request cannot be completed.
    """
    last_error: Exception | None = None

    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        transport=transport,
    ) as client:
        for _ in range(max(1, retries)):
            try:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code < 500:
                    raise ApiError(
                        f"GET {url} failed with status {exc.response.status_code}"
                    ) from exc
            except httpx.HTTPError as exc:
                last_error = exc

    raise ApiError(f"GET {url} failed after {retries} attempts") from last_error
