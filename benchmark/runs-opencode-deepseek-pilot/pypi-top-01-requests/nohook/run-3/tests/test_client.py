from __future__ import annotations

import json

import pytest
import requests

from api_fetcher.client import fetch, fetch_json


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.raised = False

    def raise_for_status(self):
        self.raised = True
        if self.status_code >= 400:
            raise requests.HTTPError("{} error".format(self.status_code))

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.closed = False

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response

    def close(self):
        self.closed = True


def test_fetch_passes_options_and_checks_status():
    response = FakeResponse({"ok": True})
    session = FakeSession(response)

    result = fetch(
        "https://example.test/items",
        params={"q": "1"},
        headers={"Accept": "application/json"},
        timeout=5,
        session=session,
    )

    assert result is response
    assert response.raised is True
    url, kwargs = session.calls[0]
    assert url == "https://example.test/items"
    assert kwargs["params"] == {"q": "1"}
    assert kwargs["headers"] == {"Accept": "application/json"}
    assert kwargs["timeout"] == 5


def test_fetch_json_decodes_body():
    session = FakeSession(FakeResponse([1, 2, 3]))
    assert fetch_json("https://example.test/nums", session=session) == [1, 2, 3]


def test_fetch_raises_on_http_error():
    session = FakeSession(FakeResponse({}, status_code=404))
    with pytest.raises(requests.HTTPError):
        fetch("https://example.test/missing", session=session)


def test_provided_session_is_not_closed():
    session = FakeSession(FakeResponse({}))
    fetch("https://example.test/keep", session=session)
    assert session.closed is False


def test_cli_prints_json(monkeypatch, capsys):
    from api_fetcher import __main__ as cli

    monkeypatch.setattr(cli, "fetch_json", lambda *a, **k: {"hello": "world"})
    assert cli.main(["https://example.test/greet"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"hello": "world"}


def test_cli_reports_failure(monkeypatch, capsys):
    from api_fetcher import __main__ as cli

    def boom(*args, **kwargs):
        raise requests.ConnectionError("no route")

    monkeypatch.setattr(cli, "fetch_json", boom)
    assert cli.main(["https://example.test/down"]) == 1
    assert "no route" in capsys.readouterr().err
