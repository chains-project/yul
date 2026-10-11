"""Encode and decode internationalized domain names (IDNA)."""

from __future__ import annotations

import idna

__all__ = ["encode", "decode", "IDNAError"]

IDNAError = idna.IDNAError


def encode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) form.

    Flags are passed through to :func:`idna.encode`; see the ``idna``
    documentation for their meaning.
    """
    return idna.encode(
        domain,
        uts46=uts46,
        std3_rules=std3_rules,
    ).decode("ascii")


def decode(
    domain: str | bytes,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
) -> str:
    """Decode an ASCII (A-label) domain name to its Unicode (U-label) form."""
    return idna.decode(
        domain,
        uts46=uts46,
        std3_rules=std3_rules,
    )
