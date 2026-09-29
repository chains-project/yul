"""IDNA (Internationalized Domain Names) encoding and decoding."""

from .core import IDNAError, Profile, decode, encode

__all__ = ["IDNAError", "Profile", "decode", "encode"]
__version__ = "0.1.0"
