import ssl
from pathlib import Path

from ca_verify import ca_bundle_path, ca_bundle_pem, ssl_context


def test_bundle_path_exists():
    assert Path(ca_bundle_path()).is_file()


def test_bundle_contains_pem_certificates():
    pem = ca_bundle_pem()
    assert b"-----BEGIN CERTIFICATE-----" in pem
    assert pem.count(b"-----BEGIN CERTIFICATE-----") > 50


def test_ssl_context_trusts_bundled_roots():
    ctx = ssl_context()
    assert isinstance(ctx, ssl.SSLContext)
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.check_hostname is True
    assert len(ctx.get_ca_certs()) > 50
