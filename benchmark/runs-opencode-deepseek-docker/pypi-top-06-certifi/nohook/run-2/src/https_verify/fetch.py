"""Fetch HTTPS resources with certificate verification enabled."""

from __future__ import annotations

import ssl
from urllib.request import Request, urlopen

from .ca_bundle import create_ssl_context

USER_AGENT = "https-verify/0.1"


def fetch(
    url: str,
    *,
    timeout: float = 30.0,
    context: ssl.SSLContext | None = None,
) -> bytes:
    """Fetch ``url`` over HTTPS, verifying the server against the CA bundle.

    Args:
        url: An ``https://`` URL. Plain HTTP is rejected outright.
        timeout: Socket timeout in seconds.
        context: Optional pre-built context, e.g. for tests.

    Returns:
        The response body as bytes.

    Raises:
        ValueError: If ``url`` is not HTTPS.
        ssl.SSLError: If the server certificate fails verification.
        urllib.error.URLError: For network-level failures.
    """
    if not url.lower().startswith("https://"):
        raise ValueError(f"refusing to fetch non-HTTPS URL: {url!r}")

    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(
        request,
        timeout=timeout,
        context=context or create_ssl_context(),
    ) as response:
        return response.read()
