"""Encode and decode internationalized domain names.

The implementation follows IDNA2008 (RFC 5890-5895) and is backed by the
reference ``idna`` package. UTS #46 processing is available as an opt-in for
handling user supplied input that may contain uppercase or otherwise
mappable characters.
"""

from __future__ import annotations

import idna

__all__ = [
    "IDNAError",
    "decode",
    "decode_label",
    "encode",
    "encode_label",
    "is_idn",
]

IDNAError = idna.IDNAError


def encode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = True,
    transitional: bool = False,
    strict: bool = False,
) -> str:
    """Encode ``domain`` to its ASCII (A-label) representation.

    ``例え.テスト`` becomes ``xn--r8jz45g.xn--zckzah``.

    Args:
        domain: A Unicode domain name.
        uts46: Apply UTS #46 processing before IDNA2008.
        std3_rules: Enforce the STD3 ASCII rules for host names.
        transitional: Use transitional UTS #46 processing (only with ``uts46``).
        strict: Raise on trailing/leading hyphens and other lax inputs.

    Raises:
        IDNAError: If ``domain`` is not a valid domain name.
    """
    if not isinstance(domain, str):
        raise IDNAError("domain must be a str")
    try:
        encoded = idna.encode(
            domain,
            strict=strict,
            uts46=uts46,
            std3_rules=std3_rules,
            transitional=transitional,
        )
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc
    return encoded.decode("ascii")


def decode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = True,
    strict: bool = False,
    display: bool = False,
) -> str:
    """Decode an ASCII (A-label) ``domain`` to its Unicode form.

    ``xn--r8jz45g.xn--zckzah`` becomes ``例え.テスト``.

    Args:
        domain: An ASCII domain name.
        uts46: Apply UTS #46 processing while decoding.
        std3_rules: Enforce the STD3 ASCII rules for host names.
        strict: Raise on trailing/leading hyphens and other lax inputs.
        display: Best-effort decoding for display; suppresses some errors.

    Raises:
        IDNAError: If ``domain`` is not a valid domain name.
    """
    if not isinstance(domain, str):
        raise IDNAError("domain must be a str")
    try:
        return idna.decode(
            domain,
            strict=strict,
            uts46=uts46,
            std3_rules=std3_rules,
            display=display,
        )
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc


def encode_label(label: str) -> str:
    """Encode a single label to its ASCII A-label form."""
    try:
        return idna.alabel(label).decode("ascii")
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc


def decode_label(label: str) -> str:
    """Decode a single ASCII label to its Unicode form."""
    try:
        return idna.ulabel(label)
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc


def is_idn(domain: str) -> bool:
    """Return ``True`` if ``domain`` is already or contains an IDN label."""
    try:
        domain.encode("ascii")
    except UnicodeEncodeError:
        return True
    return any(part.lower().startswith("xn--") for part in domain.split(".") if part)
