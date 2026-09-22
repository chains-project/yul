"""Public package interface for :mod:`httpclient`."""

from .client import HttpClient, build_default_client

__all__ = ["HttpClient", "build_default_client"]
