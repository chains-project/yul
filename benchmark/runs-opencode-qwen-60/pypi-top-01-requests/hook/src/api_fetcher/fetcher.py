"""Fetcher module for making HTTP requests to a REST API."""

import requests


class ApiFetcher:
    """Sends HTTP requests to a REST API and returns parsed JSON responses."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, endpoint: str, params: dict | None = None, limit: int | None = None) -> list:
        """Send a GET request to the given endpoint and return the JSON response.

        Args:
            endpoint: API endpoint path (e.g. 'users').
            params: Optional query parameters.
            limit: Optional maximum number of items to return from the response list.

        Returns:
            Parsed JSON response as a list (or truncated list if limit is set).
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params is None:
            params = {}
        if limit is not None:
            params["limit"] = limit
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and limit is not None:
            return data[:limit]
        return data