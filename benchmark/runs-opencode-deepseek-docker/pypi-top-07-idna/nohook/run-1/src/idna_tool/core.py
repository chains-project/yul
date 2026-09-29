"""Core IDNA encoding and decoding helpers.

This module targets IDNA 2008 (RFC 5890/5891) with UTS #46 processing, as
implemented by the ``idna`` PyPI package. The standard library
``encodings.idna`` codec is intentionally avoided: it implements the obsolete
IDNA 2003 behaviour.
"""

from __future__ import annotations

import idna

__all__ = ["encode", "decode", "IDNAError"]

IDNAError = idna.IDNAError


def encode(
    domain: str,
    *,
    uts46: bool = True,
    transitional: bool = False,
    std3_rules: bool = True,
) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) representation.

    Args:
        domain: Domain name to encode, e.g. ``"Bücher.example"``.
        uts46: Apply UTS #46 mapping before encoding.
        transitional: Use transitional (IDNA 2003 compatible) processing.
        std3_rules: Enforce STD3 ASCII rules.

    Returns:
        The ACE/punycode form, e.g. ``"xn--bcher-kva.example"``.

    Raises:
        IDNAError: If the domain violates the IDNA specification.
    """
    return idna.encode(
        domain,
        uts46=uts46,
        transitional=transitional,
        std3_rules=std3_rules,
    ).decode("ascii")


def decode(
    domain: str,
    *,
    uts46: bool = True,
    std3_rules: bool = True,
) -> str:
    """Decode an ASCII domain name to its Unicode (U-label) representation.

    Args:
        domain: Domain name to decode, e.g. ``"xn--bcher-kva.example"``.
        uts46: Apply UTS #46 mapping before decoding.
        std3_rules: Enforce STD3 ASCII rules.

    Returns:
        The Unicode form, e.g. ``"Bücher.example"``.

    Raises:
        IDNAError: If the domain violates the IDNA specification.
    """
    return idna.decode(domain, uts46=uts46, std3_rules=std3_rules)
