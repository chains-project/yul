"""HTTPS fetching backed by the certifi root CA bundle.

The `certifi` package ships a curated, regularly updated bundle of root
certificates (derived from Mozilla's CA store).  Using it instead of the
operating system trust store gives scripts a consistent, up-to-date set of
roots across platforms.
"""

from __future__ import annotations

import ssl
from urllib.request import urlopen

import certifi

__all__ = ["ca_bundle_path", "ssl_context", "fetch"]


def ca_bundle_path() -> str:
    """Return the filesystem path to the bundled CA certificate file."""
    return certifi.where()


def ssl_context() -> ssl.SSLContext:
    """Create a verified TLS context that trusts the certifi bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def fetch(url: str, *, timeout: float = 30.0) -> bytes:
    """Fetch ``url`` over HTTPS, verifying the server certificate.

    Raises ``ValueError`` for non-HTTPS URLs and ``ssl.SSLError`` when the
    certificate cannot be verified against the bundled roots.
    """
    if not url.lower().startswith("https://"):
        raise ValueError(f"refusing non-HTTPS URL: {url!r}")
    with urlopen(url, context=ssl_context(), timeout=timeout) as response:
        return response.read()
