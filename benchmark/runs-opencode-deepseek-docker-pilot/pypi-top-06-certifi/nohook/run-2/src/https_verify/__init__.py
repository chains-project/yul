"""HTTPS fetching backed by an up-to-date, curated root CA bundle."""

from .ca_bundle import ca_bundle_path, create_ssl_context
from .fetch import fetch

__all__ = ["ca_bundle_path", "create_ssl_context", "fetch"]
