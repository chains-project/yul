"""IDNA (Internationalized Domain Names) encoding and decoding.

Wrapper around the reference ``idna`` implementation, which follows
IDNA2008 (RFC 5890-5895).

Two processing profiles are exposed:

* ``Profile.IDNA2008`` (default): straight IDNA2008 as specified in the
  RFCs. Input must already be valid and in Unicode Normalization Form C, and
  must not contain disallowed code points such as uppercase ASCII.
* ``Profile.UTS46``: apply the Unicode UTS #46 mapping (case folding, NFC
  normalization, ...) before IDNA2008. This is what browsers and registries
  typically use so that user-entered names such as ``Bücher.example`` work.

Unicode is used at the public boundary: :func:`encode` accepts a Unicode
domain and returns the ASCII (A-label / punycode) form; :func:`decode` does
the reverse and returns Unicode. Malformed input raises :class:`IDNAError`.
"""

from __future__ import annotations

from enum import Enum

import idna

__all__ = ["IDNAError", "Profile", "decode", "encode"]


class Profile(str, Enum):
    """Domain-name processing profile."""

    IDNA2008 = "idna2008"
    UTS46 = "uts46"


class IDNAError(ValueError):
    """Raised when a domain cannot be processed under the selected profile."""


def _options(profile: "Profile | str") -> dict:
    try:
        profile = Profile(profile)
    except ValueError as exc:
        raise IDNAError(f"unknown profile: {profile!r}") from exc
    return {"uts46": profile is Profile.UTS46}


def encode(domain: str, *, profile: "Profile | str" = Profile.IDNA2008) -> str:
    """Return the ASCII (A-label) form of an internationalized domain name.

    >>> encode("bücher.example")
    'xn--bcher-kva.example'
    """
    if not isinstance(domain, str):
        raise IDNAError("domain must be a str")
    try:
        return idna.encode(domain, **_options(profile)).decode("ascii")
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc


def decode(domain: "str | bytes", *, profile: "Profile | str" = Profile.IDNA2008) -> str:
    """Return the Unicode (U-label) form of an ASCII/punycode domain name.

    >>> decode("xn--bcher-kva.example")
    'bücher.example'
    """
    if not isinstance(domain, (str, bytes, bytearray)):
        raise IDNAError("domain must be str or bytes")
    try:
        return idna.decode(domain, **_options(profile))
    except idna.IDNAError as exc:
        raise IDNAError(str(exc)) from exc
