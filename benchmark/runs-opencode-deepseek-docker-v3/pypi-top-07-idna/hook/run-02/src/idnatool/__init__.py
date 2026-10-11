"""Encode and decode internationalized domain names per the IDNA specification."""

from .core import IDNAError, decode_domain, encode_domain

__all__ = ["IDNAError", "decode_domain", "encode_domain"]
__version__ = "0.1.0"
