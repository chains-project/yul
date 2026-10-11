"""Encode and decode internationalized domain names per IDNA 2008 / UTS #46."""

from idn_tools.core import (
    IDNAError,
    decode_domain,
    decode_label,
    encode_domain,
    encode_label,
)

__all__ = [
    "IDNAError",
    "encode_domain",
    "decode_domain",
    "encode_label",
    "decode_label",
]

__version__ = "0.1.0"
