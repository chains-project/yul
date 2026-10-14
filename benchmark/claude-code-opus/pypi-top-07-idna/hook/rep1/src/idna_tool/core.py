"""IDNA conversion helpers.

Uses the third-party ``idna`` package, which implements IDNA 2008 and the
UTS #46 compatibility mapping. Python's built-in ``"idna"`` codec is IDNA 2003
only and gives different results for some names (e.g. it maps "ß" to "ss").
"""

import idna
from idna import IDNAError


def encode(domain: str, *, uts46: bool = True, transitional: bool = False) -> str:
    """Convert a Unicode domain name to its ASCII (Punycode/A-label) form.

    With ``uts46`` enabled (the default), input is case-folded and normalized
    the way browsers do it, so "Bücher.de" is accepted. Disable it for strict
    IDNA 2008 validation of already-normalized input.
    """
    return idna.encode(domain, uts46=uts46, transitional=transitional).decode("ascii")


def decode(domain: str) -> str:
    """Convert an ASCII (A-label) domain name back to its Unicode form."""
    return idna.decode(domain)
