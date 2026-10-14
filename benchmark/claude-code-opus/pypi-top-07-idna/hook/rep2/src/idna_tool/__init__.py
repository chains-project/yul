"""Encode and decode internationalized domain names per IDNA 2008 (RFC 5891) with UTS #46 mapping."""

from idna_tool.core import IDNAError, decode, encode

__all__ = ["IDNAError", "decode", "encode"]
