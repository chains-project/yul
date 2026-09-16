"""Core API client for fetching data from REST APIs."""

from __future__ import annotations

import json
import logging
from functools import cached_property
from typing import Any
from urllib.parse import urljoin

import requests
from requests.exceptions import HTTPError, RequestException

log = logging.getLogger(__name__)


class APIClient:
    """Client for fetching data from a REST API over HTTP.

    Args:
        base_url: The base URL of the API (e.g. ``https://api.example.com``).
        timeout: Default request timeout in seconds.
        headers: Default headers sent with every request.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._headers = headers or {}

    @cached_property
    def session(self) -> requests.Session:
        """Return a prepared requests.Session."""
        session = requests.Session()
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "api-fetcher/0.1.0",
        }
        default_headers.update(self._headers)
        session.headers.update(default_headers)
        return session

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send a GET request to *endpoint* and return the JSON body.

        Args:
            endpoint: API path appended to :attr:`base_url`.
            params: Query-string parameters.
            headers: Optional per-request headers.
            **kwargs: Extra keyword arguments forwarded to
                :meth:`requests.Session.request`.

        Returns:
            Parsed JSON response as a Python object (dict, list, …).
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        log.info("GET %s", url)
        resp = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json()

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,  # noqa: A002 shadow builtin
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send a POST request and return the JSON body.

        Args:
            endpoint: API path appended to :attr:`base_url`.
            data: Form-encoded body.
            json: JSON-serialisable body.
            headers: Optional per-request headers.
            **kwargs: Extra keyword arguments forwarded to
                :meth:`requests.Session.request`.

        Returns:
            Parsed JSON response.
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        log.info("POST %s", url)
        resp = self.session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Convenience: fetch all pages for a list endpoint
    # ------------------------------------------------------------------

    def get_all(
        self,
        endpoint: str,
        page_param: str = "page",
        per_page_param: str = "per_page",
        per_page: int = 100,
        max_pages: int = 50,
        **kwargs: Any,
    ) -> list[Any]:
        """Paginate through *endpoint* collecting every page.

        Assumes the API uses ``page_param`` and ``per_page_param`` query
        parameters and returns lists.  Stops after ``max_pages`` pages.
        """
        all_items: list[Any] = []
        page = 1
        while page <= max_pages:
            params: dict[str, Any] = {
                page_param: page,
                per_page_param: per_page,
                **kwargs.pop("params", {}),
            }
            items = self.get(endpoint, params=params, **kwargs)
            if not items:
                break
            all_items.extend(items)
            page += 1
        log.info("Collected %d total items from %s", len(all_items), endpoint)
        return all_items

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> APIClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()