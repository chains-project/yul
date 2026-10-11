"""HTTPS verification helpers backed by an up-to-date root CA bundle."""

from .ssl_bundle import ca_bundle_path, ssl_context

__all__ = ["ca_bundle_path", "ssl_context"]
__version__ = "0.1.0"
