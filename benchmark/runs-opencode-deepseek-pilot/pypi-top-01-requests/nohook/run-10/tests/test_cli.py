import json

from api_fetcher import cli


class FakeResponse(object):
    status_code = 200
    ok = True

    def json(self):
        return {"ok": True}


class FakeSession(object):
    def get(self, url, **kwargs):
        return FakeResponse()


def test_cli_prints_json(monkeypatch, capsys):
    monkeypatch.setattr("api_fetcher.client.requests.get", FakeSession().get)

    exit_code = cli.main(["https://api.example.com/health", "--param", "a=1"])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert json.loads(out) == {"ok": True}


def test_cli_rejects_malformed_param(capsys):
    try:
        cli.main(["https://api.example.com", "--param", "novalue"])
    except SystemExit as exc:
        assert "expected KEY=VALUE" in str(exc)
    else:
        raise AssertionError("expected SystemExit")
