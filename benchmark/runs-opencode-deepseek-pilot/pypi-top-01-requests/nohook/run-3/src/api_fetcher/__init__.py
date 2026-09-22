"""A script that fetches data from a REST API over HTTP."""

from .client import build_session, fetch, fetch_json

__all__ = ["build_session", "fetch", "fetch_json"]
__version__ = "0.1.0"
