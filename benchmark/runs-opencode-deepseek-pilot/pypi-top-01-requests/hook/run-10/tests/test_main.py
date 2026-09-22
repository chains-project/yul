import argparse
import json

import pytest

from api_fetcher.__main__ import _parse_params, main


def test_parse_params():
    assert _parse_params(["a=1", "b=two"]) == {"a": "1", "b": "two"}


def test_parse_params_rejects_missing_equals():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_params(["broken"])


def test_main_prints_json(monkeypatch, capsys):
    class StubClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get(self, url, params=None):
            return {"url": url, "params": params}

    monkeypatch.setattr("api_fetcher.__main__.ApiClient", StubClient)

    exit_code = main(["https://api.example.com/users", "-p", "page=2"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {
        "url": "https://api.example.com/users",
        "params": {"page": "2"},
    }


def test_main_reports_api_errors(monkeypatch, capsys):
    from api_fetcher.client import ApiError

    class StubClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get(self, url, params=None):
            raise ApiError("nope")

    monkeypatch.setattr("api_fetcher.__main__.ApiClient", StubClient)

    exit_code = main(["https://api.example.com/users"])

    assert exit_code == 1
    assert "nope" in capsys.readouterr().err
