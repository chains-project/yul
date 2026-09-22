"""Fetch data from a REST API over HTTP."""

from .client import ApiError, fetch_json

__all__ = ["ApiError", "fetch_json"]
__version__ = "0.1.0"
