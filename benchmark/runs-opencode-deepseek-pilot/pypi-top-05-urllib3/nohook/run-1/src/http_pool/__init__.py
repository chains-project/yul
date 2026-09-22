"""Low-level HTTP client built on urllib3.

Provides connection pooling (:class:`urllib3.PoolManager`) and automatic
retries (:class:`urllib3.util.Retry`) with a small, typed wrapper.
"""

from .client import DEFAULT_RETRY, HTTPError, HttpClient

__all__ = ["HttpClient", "HTTPError", "DEFAULT_RETRY"]
__version__ = "0.1.0"
