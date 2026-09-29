import ssl
from pathlib import Path

import certifi

from secure_https import ca_bundle_path, create_context


def test_bundle_matches_certifi_and_exists():
    path = ca_bundle_path()
    assert path == certifi.where()
    assert Path(path).is_file()


def test_bundle_contains_root_certificates():
    text = Path(ca_bundle_path()).read_text(encoding="utf-8")
    assert text.count("BEGIN CERTIFICATE") > 1


def test_context_enables_verification():
    context = create_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.cert_store_stats()["x509_ca"] > 0
