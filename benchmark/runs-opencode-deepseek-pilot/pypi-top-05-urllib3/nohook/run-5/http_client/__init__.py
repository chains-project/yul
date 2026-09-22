"""Low-level HTTP client built on urllib3.

Provides connection pooling, automatic retries with backoff, and fine-grained
control over timeouts and TLS verification.
"""

from .client import HttpClient, default_retry

__all__ = ["HttpClient", "default_retry"]
__version__ = "0.1.0"
