"""Core IDNA conversion helpers."""

from __future__ import annotations

import idna


def encode(domain: str, *, uts46: bool = True) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) form.

    With ``uts46`` enabled, transitional processing and non-IDNA2008
    compatibility mappings are applied before encoding.
    """
    return idna.encode(domain, uts46=uts46).decode("ascii")


def decode(domain: str, *, uts46: bool = True) -> str:
    """Decode an ASCII (A-label) domain name to its Unicode form."""
    return idna.decode(domain, uts46=uts46)
