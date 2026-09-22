"""Small client for fetching data from a REST API over HTTP."""

from .client import DEFAULT_TIMEOUT, ApiClient, ApiError, fetch_json

__all__ = ["ApiClient", "ApiError", "fetch_json", "DEFAULT_TIMEOUT"]
__version__ = "0.1.0"
