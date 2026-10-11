from __future__ import annotations

import ssl

import certifi
import pytest

from secure_fetch import ca_bundle_path, fetch, ssl_context


def test_ca_bundle_path_points_at_existing_file():
    path = ca_bundle_path()
    assert path == certifi.where()
    with open(path, "rb") as bundle:
        assert b"BEGIN CERTIFICATE" in bundle.read()


def test_ssl_context_trusts_certifi_bundle():
    context = ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_fetch_rejects_plain_http():
    with pytest.raises(ValueError):
        fetch("http://example.com")
