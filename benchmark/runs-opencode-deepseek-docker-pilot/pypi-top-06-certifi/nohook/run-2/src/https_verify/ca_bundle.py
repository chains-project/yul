"""Access the curated root CA bundle used for TLS certificate verification.

The bundle is provided by :mod:`certifi`, which repackages Mozilla's CA
Program root store and publishes a fresh release whenever that store changes.
Keeping ``certifi`` pinned and periodically upgraded is therefore what keeps
this bundle "reliable and up to date".
"""

from __future__ import annotations

import ssl
from pathlib import Path

import certifi


def ca_bundle_path() -> Path:
    """Return the filesystem path to the curated root CA bundle."""
    return Path(certifi.where())


def create_ssl_context() -> ssl.SSLContext:
    """Create a strict, modern ``SSLContext`` backed by the curated bundle."""
    return ssl.create_default_context(cafile=ca_bundle_path())
