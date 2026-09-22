"""Low-level HTTP client built on urllib3."""

from http_client.client import HttpClient
from http_client.retries import DEFAULT_RETRIES

__all__ = ["HttpClient", "DEFAULT_RETRIES"]
__version__ = "0.1.0"
