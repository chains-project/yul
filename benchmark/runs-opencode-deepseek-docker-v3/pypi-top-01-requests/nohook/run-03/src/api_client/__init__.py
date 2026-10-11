"""Fetch data from a REST API over HTTP."""

from api_client.client import APIClient
from api_client.exceptions import APIError

__all__ = ["APIClient", "APIError"]
