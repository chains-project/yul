"""Low-level HTTP client helpers: pooled connections with automatic retries."""

from .client import (
    DEFAULT_RETRY_STATUSES,
    HttpClient,
    build_retry,
    build_session,
)

__all__ = [
    "DEFAULT_RETRY_STATUSES",
    "HttpClient",
    "build_retry",
    "build_session",
]
