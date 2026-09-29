"""Tools for encoding and decoding internationalized domain names."""

from .core import (
    IDNAError,
    decode,
    decode_label,
    encode,
    encode_label,
    is_idn,
)

__all__ = [
    "IDNAError",
    "decode",
    "decode_label",
    "encode",
    "encode_label",
    "is_idn",
]

__version__ = "0.1.0"
