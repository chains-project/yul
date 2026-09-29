import ssl

import certifi

from secure_fetch import build_ssl_context, fetch


def test_certifi_bundle_exists():
    assert certifi.where()
    with open(certifi.where(), "rb") as handle:
        assert b"BEGIN CERTIFICATE" in handle.read()


def test_build_ssl_context_verifies():
    context = build_ssl_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.cert_store_stats()["x509_ca"] > 0


def test_main_writes_body(monkeypatch, capsys):
    import secure_fetch.cli as cli

    monkeypatch.setattr(cli, "fetch", lambda url, **kwargs: b"hello")
    assert cli.main(["https://example.com"]) == 0
    assert capsys.readouterr().out == "hello"


def test_main_reports_errors(monkeypatch, capsys):
    import secure_fetch.cli as cli

    def boom(url, **kwargs):
        raise ssl.SSLError("bad certificate")

    monkeypatch.setattr(cli, "fetch", boom)
    assert cli.main(["https://example.com"]) == 1
    assert "bad certificate" in capsys.readouterr().err


def test_fetch_importable():
    assert callable(fetch)
