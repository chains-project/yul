"""Encode and decode internationalized domain names per IDNA 2008."""

from .core import IDNError, decode, encode, is_idn

__all__ = ["IDNError", "decode", "encode", "is_idn"]
