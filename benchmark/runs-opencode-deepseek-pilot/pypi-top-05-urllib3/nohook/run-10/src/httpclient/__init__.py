"""Low-level HTTP client built on urllib3.

Exposes connection pooling and automatic retries directly so callers keep
fine-grained control over the underlying connections.
"""

from .client import HttpClient, HttpError

__all__ = ["HttpClient", "HttpError"]
__version__ = "0.1.0"
