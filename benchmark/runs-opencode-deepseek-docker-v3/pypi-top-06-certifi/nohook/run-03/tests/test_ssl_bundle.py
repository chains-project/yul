from pathlib import Path
import ssl

from certcheck.ssl_bundle import ca_bundle_path, ssl_context


def test_bundle_file_exists_and_is_not_empty():
    bundle = Path(ca_bundle_path())
    assert bundle.is_file()
    assert bundle.stat().st_size > 0


def test_bundle_contains_root_certificates():
    context = ssl_context()
    stats = context.cert_store_stats()
    assert stats["x509_ca"] > 0


def test_context_enforces_verification():
    context = ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_bundle_path_is_cached():
    assert ca_bundle_path() is ca_bundle_path()
