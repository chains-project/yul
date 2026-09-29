"""Encode and decode internationalized domain names per IDNA (RFC 5891)."""

from .core import Codec, IDNAError, decode, encode

__all__ = ["Codec", "IDNAError", "decode", "encode"]
__version__ = "0.1.0"
