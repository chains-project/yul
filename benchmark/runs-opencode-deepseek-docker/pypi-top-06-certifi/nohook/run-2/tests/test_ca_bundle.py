import ssl

import pytest

from https_verify import ca_bundle_path, create_ssl_context
from https_verify.fetch import fetch


def test_bundle_file_is_present_and_non_empty():
    path = ca_bundle_path()
    assert path.is_file()
    assert path.stat().st_size > 0


def test_bundle_contains_roots():
    contents = ca_bundle_path().read_text(encoding="utf-8", errors="replace")
    assert contents.count("BEGIN CERTIFICATE") > 0


def test_context_requires_certificate_verification():
    context = create_ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_fetch_rejects_plain_http():
    with pytest.raises(ValueError):
        fetch("http://example.com/")
