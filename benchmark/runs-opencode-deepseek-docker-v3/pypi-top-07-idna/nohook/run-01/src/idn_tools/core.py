"""Core IDNA encoding and decoding helpers.

This module wraps the ``idna`` package, which implements IDNA 2008
(RFC 5890/5891/5892) and the UTS #46 compatibility processing. That is a
strictly more modern and correct implementation than the IDNA 2003 codec
built into the Python standard library (``str.encode("idna")``).
"""

from __future__ import annotations

from typing import Union

import idna

IDNAError = idna.IDNAError
DomainLike = Union[str, bytes]


def _as_text(domain: DomainLike) -> str:
    if isinstance(domain, bytes):
        return domain.decode("ascii")
    if isinstance(domain, str):
        return domain
    raise TypeError(f"domain must be str or bytes, not {type(domain).__name__}")


def encode_domain(
    domain: DomainLike,
    *,
    uts46: bool = True,
) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) form.

    Each label is converted to Punycode with an ``xn--`` prefix. Labels that
    are already ASCII are validated and passed through unchanged.

    Args:
        domain: The domain name, as ``str`` (Unicode or ASCII) or ASCII
            ``bytes``.
        uts46: Apply UTS #46 mapping (case folding, normalization, etc.)
            before encoding. Enabled by default.

    Returns:
        The ASCII (A-label) representation of the domain.

    Raises:
        IDNAError: If the domain is empty or contains a label that is not
            valid under the IDNA rules.
        TypeError: If ``domain`` is neither ``str`` nor ``bytes``.
    """
    text = _as_text(domain)
    if not text:
        raise IDNAError("empty domain")
    return idna.encode(
        text,
        uts46=uts46,
        std3_rules=True,
    ).decode("ascii")


def decode_domain(domain: DomainLike, *, uts46: bool = True) -> str:
    """Decode an ASCII (A-label) domain name to its Unicode (U-label) form.

    Args:
        domain: The domain name in ASCII form, as ``str`` or ASCII ``bytes``.
        uts46: Validate and map the decoded result using UTS #46.

    Returns:
        The Unicode representation of the domain.

    Raises:
        IDNAError: If the domain is invalid or fails IDNA validation.
        TypeError: If ``domain`` is neither ``str`` nor ``bytes``.
    """
    raw = domain.encode("ascii") if isinstance(domain, str) else domain
    if not isinstance(raw, bytes):
        raise TypeError(f"domain must be str or bytes, not {type(domain).__name__}")
    if not raw:
        raise IDNAError("empty domain")
    return idna.decode(raw, uts46=uts46)


def encode_label(label: str, *, uts46: bool = True) -> str:
    """Encode a single Unicode label to its ASCII (A-label) form."""
    if not isinstance(label, str):
        raise TypeError(f"label must be str, not {type(label).__name__}")
    if uts46:
        label = idna.uts46_remap(label, std3_rules=True)
    return idna.alabel(label).decode("ascii")


def decode_label(label: DomainLike, *, uts46: bool = True) -> str:
    """Decode a single ASCII (A-label) label to its Unicode (U-label) form."""
    text = _as_text(label)
    result = idna.ulabel(text)
    if uts46:
        result = idna.uts46_remap(result, std3_rules=True)
    return result
