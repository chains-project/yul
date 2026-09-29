"""Internationalized domain name (IDNA) encoding and decoding helpers."""

from idn_tool.core import (
    IDNAError,
    decode,
    encode,
    to_ascii,
    to_unicode,
)

__all__ = [
    "IDNAError",
    "decode",
    "encode",
    "to_ascii",
    "to_unicode",
]

__version__ = "0.1.0"
