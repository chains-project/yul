"""Encode and decode internationalized domain names per IDNA 2008 (RFC 5891).

Uses the third-party ``idna`` package rather than Python's built-in ``"idna"``
codec, which only implements the obsolete IDNA 2003 standard.
"""

import idna

__all__ = ["encode", "decode", "IDNAError"]

IDNAError = idna.IDNAError


def encode(domain: str, *, uts46: bool = True) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode, ``xn--``) form.

    With ``uts46`` enabled (the default), input is normalized first per UTS #46
    (e.g. case-folding), matching how browsers treat user-entered names.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (``xn--``) domain name to its Unicode form."""
    return idna.decode(domain)
