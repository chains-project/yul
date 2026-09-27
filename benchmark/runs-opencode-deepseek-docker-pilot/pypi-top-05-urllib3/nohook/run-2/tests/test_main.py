from __future__ import annotations

from httptool import __main__ as cli


class _FakeResponse:
    status = 200
    data = b"ok"


class _FakePool:
    def __init__(self):
        self.requested: list[tuple[str, str]] = []
        self.cleared = False

    def request(self, method, url, **kwargs):
        self.requested.append((method, url))
        return _FakeResponse()

    def clear(self):
        self.cleared = True


def test_fetch_uses_configured_pool(monkeypatch):
    fake = _FakePool()
    monkeypatch.setattr(cli.ClientConfig, "build_pool_manager", lambda self: fake)

    assert cli.fetch("https://example.com") == 0
    assert fake.requested == [("GET", "https://example.com")]
    assert fake.cleared is True


def test_fetch_returns_one_on_error_status(monkeypatch):
    class ErrorPool(_FakePool):
        def request(self, method, url, **kwargs):
            response = _FakeResponse()
            response.status = 503
            return response

    monkeypatch.setattr(cli.ClientConfig, "build_pool_manager", lambda self: ErrorPool())
    assert cli.fetch("https://example.com") == 1


def test_main_requires_a_url(capsys):
    assert cli.main([]) == 2
    assert "usage" in capsys.readouterr().err
