"""Encode and decode internationalized domain names per IDNA 2008 / UTS #46."""

from idna_tool.codec import decode, encode

__all__ = ["encode", "decode"]
