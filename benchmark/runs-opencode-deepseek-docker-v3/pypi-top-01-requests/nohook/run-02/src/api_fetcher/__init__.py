"""Fetch data from a REST API over HTTP."""

from api_fetcher.client import ApiError, ApiResponse, fetch

__all__ = ["ApiError", "ApiResponse", "fetch"]
__version__ = "0.1.0"
