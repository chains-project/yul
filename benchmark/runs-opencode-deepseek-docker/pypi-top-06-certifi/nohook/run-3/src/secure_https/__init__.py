"""HTTPS helpers that verify servers against an up-to-date root CA bundle."""

from .context import ca_bundle_path, create_context

__all__ = ["ca_bundle_path", "create_context"]
