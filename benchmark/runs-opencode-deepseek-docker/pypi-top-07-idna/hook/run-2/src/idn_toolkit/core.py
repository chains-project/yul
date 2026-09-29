"""Core IDNA encoding and decoding.

The heavy lifting is delegated to the ``idna`` package, the reference
implementation of IDNA2008 (RFC 5891 / RFC 5892). By default processing is
strict IDNA2008; pass ``uts46=True`` to apply the UTS #46 mapping (case
folding, NFC normalization, ...) that browsers use for compatibility.
"""

from __future__ import annotations

import idna

__all__ = [
    "IDNABidiError",
    "IDNAError",
    "InvalidCodepoint",
    "decode",
    "encode",
]

IDNAError = idna.IDNAError
IDNABidiError = idna.IDNABidiError
InvalidCodepoint = idna.InvalidCodepoint


def encode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
    transitional: bool = False,
) -> str:
    """Return the ASCII (A-label / punycode) form of a Unicode domain name.

    Raises :class:`IDNAError` (or a subclass) if the domain is not valid.
    """
    if not isinstance(domain, str):
        raise TypeError("domain must be a str")
    result = idna.encode(
        domain,
        uts46=uts46,
        std3_rules=std3_rules,
        transitional=transitional,
    )
    return result.decode("ascii")


def decode(
    domain: str | bytes,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
) -> str:
    """Return the Unicode (U-label) form of an ASCII domain name.

    Raises :class:`IDNAError` (or a subclass) if the domain is not valid.
    """
    if isinstance(domain, bytes):
        domain = domain.decode("ascii")
    if not isinstance(domain, str):
        raise TypeError("domain must be a str or bytes")
    return idna.decode(domain, uts46=uts46, std3_rules=std3_rules)
