"""IDNA conversion helpers.

Uses the third-party ``idna`` package rather than Python's built-in ``"idna"``
codec, which only implements the obsolete IDNA 2003 standard.
"""

import idna

IDNAError = idna.IDNAError


def encode(domain: str, *, uts46: bool = True) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode/A-label) form.

    With ``uts46`` enabled (the default), input is first normalized per
    UTS #46 (e.g. case folding), matching how browsers treat user input.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (A-label) domain name back to its Unicode form."""
    return idna.decode(domain)
