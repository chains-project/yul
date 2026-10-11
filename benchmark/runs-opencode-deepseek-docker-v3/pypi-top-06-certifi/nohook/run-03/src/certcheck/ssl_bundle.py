"""Access the bundled Mozilla root certificate store.

`certifi` is a curated copy of Mozilla's CA bundle. Keeping it as a runtime
dependency (rather than relying on the interpreter's or OS default trust store)
gives a consistent, up-to-date set of roots across platforms. Run
``python -m pip install --upgrade certifi`` to refresh the bundle.
"""

from __future__ import annotations

import ssl
from functools import lru_cache

import certifi


@lru_cache(maxsize=1)
def ca_bundle_path() -> str:
    """Return the filesystem path to the current CA bundle."""
    return certifi.where()


@lru_cache(maxsize=1)
def ssl_context() -> ssl.SSLContext:
    """Return a strict TLS client context using the bundled roots."""
    context = ssl.create_default_context(cafile=ca_bundle_path())
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context
