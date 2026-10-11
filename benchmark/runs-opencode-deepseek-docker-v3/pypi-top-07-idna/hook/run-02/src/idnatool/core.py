"""Core IDNA encoding and decoding helpers.

The heavy lifting is delegated to the ``idna`` package, which implements the
IDNA 2008 specification (RFC 5890-5895) and the UTS #46 compatibility
processing rules.  This module adds domain-level conveniences such as
trailing-dot (fully qualified domain name) handling and consistent string
in/out semantics.
"""

from __future__ import annotations

import idna

__all__ = ["IDNAError", "decode_domain", "encode_domain"]

IDNAError = idna.IDNAError

_DOTS = ("\u3002", "\uff0e", "\uff61", ".")


def _split_trailing_dot(domain: str) -> tuple[str, bool]:
    if domain and domain[-1] in _DOTS:
        return domain[:-1], True
    return domain, False


def encode_domain(
    domain: str,
    *,
    uts46: bool = True,
    strict: bool = False,
    std3_rules: bool = False,
) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) form.

    Labels are converted to Punycode A-labels and lowercased.  A single
    trailing dot is preserved so that fully qualified names round-trip.

    Args:
        domain: The Unicode domain name, e.g. ``"例え.テスト"``.
        uts46: Apply UTS #46 mapping and normalization. Enabled by default
            because it provides the expected browser-like behaviour.
        strict: Disallow certain deviations from the specification.
        std3_rules: Enforce STD3 ASCII rules on the input.

    Returns:
        The encoded ASCII domain name, e.g. ``"xn--r8jz45g.xn--zckzah"``.

    Raises:
        idna.IDNAError: If the domain is not a valid IDN.
    """
    if not isinstance(domain, str):
        raise TypeError(f"domain must be str, not {type(domain).__name__}")

    body, had_dot = _split_trailing_dot(domain)
    if body == "":
        return "." if had_dot else ""

    encoded = idna.encode(
        body,
        uts46=uts46,
        strict=strict,
        std3_rules=std3_rules,
    ).decode("ascii")

    return encoded + "." if had_dot else encoded


def decode_domain(
    domain: str,
    *,
    uts46: bool = True,
    strict: bool = False,
    std3_rules: bool = False,
) -> str:
    """Decode an ASCII (A-label) domain name to its Unicode form.

    Args:
        domain: The ASCII domain name, e.g. ``"xn--r8jz45g.xn--zckzah"``.
        uts46: Apply UTS #46 mapping and normalization. Enabled by default.
        strict: Disallow certain deviations from the specification.
        std3_rules: Enforce STD3 ASCII rules on the input.

    Returns:
        The decoded Unicode domain name, e.g. ``"例え.テスト"``.

    Raises:
        idna.IDNAError: If the domain is not a valid IDN.
    """
    if not isinstance(domain, str):
        raise TypeError(f"domain must be str, not {type(domain).__name__}")

    body, had_dot = _split_trailing_dot(domain)
    if body == "":
        return "." if had_dot else ""

    decoded = idna.decode(
        body,
        uts46=uts46,
        strict=strict,
        std3_rules=std3_rules,
    )

    return decoded + "." if had_dot else decoded
