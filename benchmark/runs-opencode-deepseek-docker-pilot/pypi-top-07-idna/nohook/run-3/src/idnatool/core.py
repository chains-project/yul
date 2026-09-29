"""Core IDNA encoding and decoding helpers.

This module wraps the :mod:`idna` package, which implements IDNA 2008
(RFC 5891), with a small, typed API for converting domain names between their
Unicode and ASCII (A-label) representations.

Note:
    The standard-library ``encodings.idna`` codec implements the obsolete
    IDNA 2003 specification and rejects or mis-maps many modern names. Use this
    module instead when correct IDNA 2008 behaviour matters.
"""

from __future__ import annotations

from dataclasses import dataclass

import idna


class IDNAError(ValueError):
    """Raised when a domain name cannot be encoded or decoded."""


@dataclass(frozen=True)
class Codec:
    """A configurable IDNA codec.

    Attributes:
        uts46: Apply UTS #46 processing (mapping and normalization) before
            encoding, and normalization when decoding.
        std3_rules: Enforce STD3 ASCII rules, restricting the characters
            permitted in a label.
    """

    uts46: bool = True
    std3_rules: bool = False

    def encode(self, domain: str) -> str:
        """Encode a Unicode *domain* to its ASCII A-label form.

        Args:
            domain: A Unicode domain name, e.g. ``"münchen.de"``. A trailing
                root dot is preserved.

        Returns:
            The ASCII-compatible encoding, e.g. ``"xn--mnchen-3ya.de"``.

        Raises:
            IDNAError: If *domain* is not a valid IDNA domain name.
        """
        try:
            return idna.encode(
                domain,
                uts46=self.uts46,
                std3_rules=self.std3_rules,
            ).decode("ascii")
        except idna.IDNAError as exc:
            raise IDNAError(str(exc)) from exc

    def decode(self, domain: str) -> str:
        """Decode an ASCII *domain* containing A-labels to Unicode.

        Args:
            domain: An ASCII domain name, e.g. ``"xn--mnchen-3ya.de"``. ASCII
                labels are returned unchanged; A-labels are decoded.

        Returns:
            The Unicode domain name, e.g. ``"münchen.de"``.

        Raises:
            IDNAError: If *domain* is not a valid IDNA domain name.
        """
        try:
            return idna.decode(
                domain,
                uts46=self.uts46,
                std3_rules=self.std3_rules,
            )
        except idna.IDNAError as exc:
            raise IDNAError(str(exc)) from exc


def encode(
    domain: str,
    *,
    uts46: bool = True,
    std3_rules: bool = False,
) -> str:
    """Encode a Unicode domain name to its ASCII A-label form.

    Convenience wrapper around :class:`Codec`.
    """
    return Codec(uts46=uts46, std3_rules=std3_rules).encode(domain)


def decode(
    domain: str,
    *,
    uts46: bool = True,
    std3_rules: bool = False,
) -> str:
    """Decode an ASCII domain name (with A-labels) to Unicode.

    Convenience wrapper around :class:`Codec`.
    """
    return Codec(uts46=uts46, std3_rules=std3_rules).decode(domain)
