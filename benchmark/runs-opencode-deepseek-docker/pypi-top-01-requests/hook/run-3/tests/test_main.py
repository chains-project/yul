import json

from api_fetcher import __main__ as cli
from api_fetcher.client import ApiError


def test_main_prints_pretty_json(capsys, monkeypatch):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def get(self, path="", *, params=None):
            return {"name": "ada", "id": 1}

    monkeypatch.setattr(cli, "ApiClient", FakeClient)

    assert cli.main(["https://api.example.com/users"]) == 0
    assert json.loads(capsys.readouterr().out) == {"name": "ada", "id": 1}


def test_main_reports_errors(capsys, monkeypatch):
    class FailingClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def get(self, path="", *, params=None):
            raise ApiError("kaboom")

    monkeypatch.setattr(cli, "ApiClient", FailingClient)

    assert cli.main(["https://api.example.com"]) == 1
    assert "kaboom" in capsys.readouterr().err
