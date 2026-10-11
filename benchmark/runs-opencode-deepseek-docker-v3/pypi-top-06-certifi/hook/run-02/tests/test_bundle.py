from __future__ import annotations

import ssl
from pathlib import Path

from ca_bundle import ca_bundle_path, create_ssl_context


def test_bundle_exists_and_is_nonempty() -> None:
    path = Path(ca_bundle_path())
    assert path.is_file()
    assert path.stat().st_size > 0


def test_bundle_contains_a_root_store() -> None:
    text = Path(ca_bundle_path()).read_text(encoding="utf-8")
    assert text.count("BEGIN CERTIFICATE") >= 100


def test_context_verifies_peers_by_default() -> None:
    context = create_ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.get_ca_certs()
