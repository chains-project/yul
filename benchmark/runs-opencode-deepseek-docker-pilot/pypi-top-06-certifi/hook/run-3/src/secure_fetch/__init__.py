"""HTTPS fetching backed by certifi's up-to-date root CA bundle."""

from secure_fetch.cli import build_ssl_context, fetch

__all__ = ["build_ssl_context", "fetch"]
__version__ = "0.1.0"
