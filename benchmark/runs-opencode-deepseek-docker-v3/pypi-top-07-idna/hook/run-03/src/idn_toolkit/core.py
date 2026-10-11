"""IDNA (Internationalized Domain Names in Applications) helpers.

Wraps the `idna` package to operate on whole domain names rather than
individual labels. Implements IDNA2008 as specified in RFC 5890/5891.
"""

from __future__ import annotations

import idna as _idna

__all__ = ["encode", "decode", "IDNError"]

IDNError = _idna.IDNAError


def _split(domain: str) -> tuple[list[str], bool]:
    if not isinstance(domain, str):
        raise TypeError("domain must be a str")
    if domain == "":
        return [], False
    trailing_dot = domain.endswith(".")
    labels = domain[:-1].split(".") if trailing_dot else domain.split(".")
    return labels, trailing_dot


def _apply(labels: list[str], trailing_dot: bool, func) -> str:
    encoded = []
    for label in labels:
        if label == "":
            raise IDNError("empty label encountered in domain name")
        encoded.append(func(label))
    result = ".".join(encoded)
    if trailing_dot:
        result += "."
    return result


def encode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
    transitional: bool = False,
) -> str:
    """Encode a Unicode domain name to its ASCII (A-label) form."""
    labels, trailing_dot = _split(domain)
    return _apply(
        labels,
        trailing_dot,
        lambda label: _idna.encode(
            label,
            uts46=uts46,
            std3_rules=std3_rules,
            transitional=transitional,
        ).decode("ascii"),
    )


def decode(
    domain: str,
    *,
    uts46: bool = False,
    std3_rules: bool = False,
) -> str:
    """Decode an ASCII (A-label) or Unicode domain name to its Unicode form."""
    labels, trailing_dot = _split(domain)
    return _apply(
        labels,
        trailing_dot,
        lambda label: _idna.decode(
            label,
            uts46=uts46,
            std3_rules=std3_rules,
        ),
    )
