"""Access to a reliable, up-to-date bundle of root CA certificates.

The bundle is provided by :mod:`certifi`, which ships the curated Mozilla CA
root store and is updated as roots are added or revoked.
"""

from __future__ import annotations

import ssl
from pathlib import Path

import certifi

__all__ = ["ca_bundle_path", "ca_bundle_pem", "ssl_context"]


def ca_bundle_path() -> str:
    """Return the path to certifi's bundled Mozilla CA root certificates."""
    return certifi.where()


def ca_bundle_pem() -> bytes:
    """Return the CA root certificates as PEM-encoded bytes."""
    return Path(certifi.where()).read_bytes()


def ssl_context() -> ssl.SSLContext:
    """Return a strict client SSLContext trusting the bundled roots."""
    return ssl.create_default_context(cafile=ca_bundle_path())
