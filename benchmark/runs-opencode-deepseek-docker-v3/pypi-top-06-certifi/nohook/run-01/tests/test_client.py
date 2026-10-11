from __future__ import annotations

import ssl
from pathlib import Path

import certifi

from https_verify import ca_bundle_path, create_ssl_context
from https_verify.client import fetch


def test_ca_bundle_path_matches_certifi() -> None:
    assert ca_bundle_path() == certifi.where()
    assert Path(ca_bundle_path()).is_file()


def test_ssl_context_is_strict() -> None:
    context = create_ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_fetch_rejects_non_https() -> None:
    try:
        fetch("http://example.com")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for non-HTTPS URL")
