"""IDNA conversion helpers.

Uses the third-party ``idna`` package rather than Python's built-in ``"idna"``
codec: the stdlib codec implements the obsolete IDNA 2003 (RFC 3490), which
e.g. maps "ß" to "ss" and so resolves to a different domain than browsers do.
"""

import idna
from idna import IDNAError

__all__ = ["IDNAError", "decode", "encode"]


def encode(domain: str, *, uts46: bool = True) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode "xn--") form.

    With ``uts46`` enabled (the default, matching browser behaviour), input is
    first normalized per UTS #46, so e.g. uppercase letters are case-folded.
    Raises ``IDNAError`` if the name is not valid under IDNA 2008.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII-compatible domain name back to Unicode.

    Raises ``IDNAError`` if any label is not valid under IDNA 2008.
    """
    return idna.decode(domain)
