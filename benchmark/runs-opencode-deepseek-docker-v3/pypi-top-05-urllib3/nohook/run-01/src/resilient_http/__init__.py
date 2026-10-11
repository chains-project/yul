"""Resilient HTTP client with connection pooling and automatic retries."""

from .session import build_session

__all__ = ["build_session"]
