"""Build SSL/TLS contexts that trust an up-to-date root CA bundle."""

from __future__ import annotations

import ssl

import certifi

__all__ = ["ca_bundle_path", "create_context"]


def ca_bundle_path() -> str:
    """Return the path to certifi's current Mozilla root CA bundle."""
    return certifi.where()


def create_context() -> ssl.SSLContext:
    """Return a verifying SSL context backed by certifi's CA bundle.

    Certificate and hostname verification are always enabled; this helper
    never disables them.
    """
    return ssl.create_default_context(cafile=ca_bundle_path())
