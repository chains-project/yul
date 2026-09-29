"""Core IDNA encode/decode operations.

This module wraps the ``idna`` package, which implements IDNA 2008
(RFC 5890/5891) and UTS #46 processing.
"""

from __future__ import annotations

import idna

IDNAError = idna.IDNAError


def encode(domain: str, *, uts46: bool = False, strict: bool = False) -> bytes:
    """Encode a Unicode domain name to its ASCII (A-label) form.

    Returns the encoded domain as ASCII bytes. Use :func:`to_ascii` for a
    ``str`` result.
    """
    return idna.encode(domain, uts46=uts46, strict=strict)


def decode(domain: str | bytes) -> str:
    """Decode an ASCII (A-label) domain name to its Unicode (U-label) form."""
    if isinstance(domain, bytes):
        domain = domain.decode("ascii")
    return idna.decode(domain)


def to_ascii(domain: str, *, uts46: bool = False, strict: bool = False) -> str:
    """Encode a Unicode domain name and return the result as ``str``."""
    return encode(domain, uts46=uts46, strict=strict).decode("ascii")


def to_unicode(domain: str | bytes) -> str:
    """Alias for :func:`decode`; returns the Unicode domain name."""
    return decode(domain)
