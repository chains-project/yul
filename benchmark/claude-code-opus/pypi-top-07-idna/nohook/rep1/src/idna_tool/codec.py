"""IDNA encode/decode helpers.

Uses the ``idna`` package (IDNA 2008, RFC 5891) rather than Python's built-in
``"idna"`` codec, which only implements the obsolete IDNA 2003.
"""

import idna


def encode(domain: str, *, uts46: bool = True) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode) form.

    With ``uts46`` enabled (the default), input is first normalized per
    UTS #46 (e.g. case folding), matching browser behavior.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (Punycode) domain name to its Unicode form."""
    return idna.decode(domain)
