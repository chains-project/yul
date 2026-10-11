from __future__ import annotations

import ssl
import urllib.request

import certifi

__all__ = ["ca_bundle_path", "create_ssl_context", "fetch"]


def ca_bundle_path() -> str:
    """Return the path to certifi's current, packaged root CA bundle."""
    return certifi.where()


def create_ssl_context() -> ssl.SSLContext:
    """Build a strict TLS client context that trusts only certifi's CA bundle.

    Hostname and certificate verification are enabled, and the context is
    pinned to the CA file shipped with the installed certifi release so the
    trust store is reproducible and easy to refresh via ``uv lock --upgrade``.
    """
    context = ssl.create_default_context(cafile=ca_bundle_path())
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


def fetch(url: str, *, timeout: float = 30.0) -> bytes:
    """Fetch ``url`` over HTTPS, verifying the peer against the CA bundle."""
    if not url.lower().startswith("https://"):
        raise ValueError(f"refusing non-HTTPS URL: {url!r}")

    request = urllib.request.Request(
        url, headers={"User-Agent": "https-verify/0.1"}
    )
    with urllib.request.urlopen(
        request, context=create_ssl_context(), timeout=timeout
    ) as response:
        return response.read()
