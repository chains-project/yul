"""httpkit: low-level HTTP with connection pooling and automatic retries."""

from .client import HTTPClient, HTTPError, RetryPolicy

__all__ = ["HTTPClient", "HTTPError", "RetryPolicy"]
__version__ = "0.1.0"
