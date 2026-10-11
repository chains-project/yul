"""Up-to-date root CA certificates for verifying HTTPS connections.

The bundle is provided by :mod:`certifi`, which ships Mozilla's CA
certificate store and is refreshed with each release. Pin a recent
``certifi`` version and upgrade it regularly to stay current.
"""

from __future__ import annotations

import ssl

import certifi

__all__ = ["ca_bundle_path", "create_ssl_context"]


def ca_bundle_path() -> str:
    """Return the filesystem path to the current CA bundle."""
    return certifi.where()


def create_ssl_context() -> ssl.SSLContext:
    """Return an SSL context that verifies peers against the CA bundle."""
    context = ssl.create_default_context(cafile=certifi.where())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context
