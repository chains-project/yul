"""Build SSL contexts that trust the bundled, up-to-date root certificates."""

from __future__ import annotations

import ssl

import certifi


def ca_bundle_path() -> str:
    """Return the path to certifi's current root CA bundle."""
    return certifi.where()


def build_ssl_context() -> ssl.SSLContext:
    """Create a verifying SSL context using certifi's CA bundle.

    The context enforces certificate and hostname verification using the
    latest Mozilla root store shipped by certifi.
    """
    context = ssl.create_default_context(cafile=certifi.where())
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    return context
