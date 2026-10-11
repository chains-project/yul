"""Encode and decode internationalized domain names under IDNA (RFC 5890-5892).

The heavy lifting is delegated to the :mod:`idna` package, which implements
IDNA 2008 plus the optional UTS #46 compatibility processing.
"""

from __future__ import annotations

import idna

__all__ = ["IDNError", "encode", "decode", "is_idn"]


class IDNError(ValueError):
    """Raised when a domain cannot be encoded or decoded."""


def encode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
) -> str:
    """Return the ASCII (A-label) form of *domain*.

    Args:
        domain: A domain name, either already ASCII or containing
            internationalized (Unicode) labels.
        uts46: Apply UTS #46 processing first. This performs case folding and
            other compatibility mappings, which is friendlier for arbitrary
            user input but is stricter than raw IDNA 2008.
        std3_rules: Enforce the STD3 ASCII rules (for example, reject
            underscores and leading/trailing hyphens).

    Raises:
        IDNError: If the domain is not a valid internationalized domain name.
    """
    if not isinstance(domain, str):
        raise TypeError("domain must be a str")

    try:
        return idna.encode(domain, uts46=uts46, std3_rules=std3_rules).decode("ascii")
    except idna.IDNAError as exc:
        raise IDNError(str(exc)) from exc


def decode(domain: str | bytes) -> str:
    """Return the Unicode (U-label) form of *domain*.

    ASCII A-labels such as ``xn--mnchen-3ya.de`` are converted back to their
    Unicode equivalents such as ``münchen.de``. Labels that are already
    Unicode are returned unchanged, so this function is idempotent.

    Raises:
        IDNError: If the domain is not a valid internationalized domain name.
    """
    if not isinstance(domain, (str, bytes)):
        raise TypeError("domain must be a str or bytes")

    try:
        return idna.decode(domain)
    except idna.IDNAError as exc:
        raise IDNError(str(exc)) from exc


def is_idn(domain: str) -> bool:
    """Return ``True`` if *domain* contains any non-ASCII characters."""
    return any(ord(char) > 127 for char in domain)
