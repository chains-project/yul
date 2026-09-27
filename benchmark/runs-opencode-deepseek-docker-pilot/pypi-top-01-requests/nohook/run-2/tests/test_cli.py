import json

import api_fetcher.__main__ as cli


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_json(self, path, *, params=None):
        return {"path": path, "params": params}


def patch_client(monkeypatch):
    monkeypatch.setattr(cli, "ApiClient", DummyClient)


def test_main_prints_json(monkeypatch, capsys):
    patch_client(monkeypatch)
    code = cli.main(["/users", "-b", "https://api.example.com", "-p", "page=2", "-p", "q=hi"])
    assert code == 0
    assert json.loads(capsys.readouterr().out) == {
        "path": "/users",
        "params": {"page": "2", "q": "hi"},
    }


def test_main_reports_api_errors(monkeypatch, capsys):
    class FailingClient(DummyClient):
        def get_json(self, path, *, params=None):
            from api_fetcher.client import ApiError

            raise ApiError("nope")

    monkeypatch.setattr(cli, "ApiClient", FailingClient)
    assert cli.main(["https://api.example.com"]) == 1
    assert "nope" in capsys.readouterr().err


def test_main_rejects_malformed_param(capsys):
    try:
        cli.main(["https://api.example.com", "-p", "broken"])
    except SystemExit as exc:
        assert "invalid --param" in str(exc)
    else:
        raise AssertionError("expected SystemExit for malformed parameter")
