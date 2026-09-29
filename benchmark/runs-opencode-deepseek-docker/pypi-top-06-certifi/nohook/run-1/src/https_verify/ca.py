from __future__ import annotations

import ssl

import certifi


def ca_bundle_path() -> str:
    return certifi.where()


def create_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=ca_bundle_path())
