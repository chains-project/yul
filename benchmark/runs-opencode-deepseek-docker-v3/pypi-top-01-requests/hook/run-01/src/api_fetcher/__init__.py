"""Fetch data from a REST API over HTTP."""

from .fetcher import ApiError, fetch

__all__ = ["ApiError", "fetch"]
