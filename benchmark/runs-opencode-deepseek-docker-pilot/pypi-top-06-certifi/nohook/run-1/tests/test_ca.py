from pathlib import Path

from https_verify import ca_bundle_path, create_context


def test_bundle_exists():
    assert Path(ca_bundle_path()).is_file()


def test_bundle_has_certificates():
    text = Path(ca_bundle_path()).read_text()
    assert "BEGIN CERTIFICATE" in text


def test_context_uses_bundle():
    context = create_context()
    assert context.verify_mode == 2
    assert context.check_hostname is True
