"""Tests for the REST client and CLI."""

import json
from unittest import mock

import pytest

from rest_fetch import ApiError, RestClient
from rest_fetch.cli import main, parse_params


def make_response(status_code=200, payload=None, content=b"{}", url="http://x/"):
    response = mock.Mock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.url = url
    response.content = content
    response.json.return_value = payload
    return response


def test_get_returns_decoded_json():
    client = RestClient("https://api.example.com")
    response = make_response(payload={"id": 1, "name": "Ada"})

    with mock.patch.object(client.session, "request", return_value=response) as req:
        data = client.get("/users/1")

    assert data == {"id": 1, "name": "Ada"}
    req.assert_called_once()
    assert req.call_args[0][:2] == ("GET", "https://api.example.com/users/1")


def test_get_passes_params():
    client = RestClient("https://api.example.com")
    response = make_response(payload=[])

    with mock.patch.object(client.session, "request", return_value=response) as req:
        client.get("/search", params={"q": "python"})

    assert req.call_args[1]["params"] == {"q": "python"}


def test_error_status_raises_api_error():
    client = RestClient("https://api.example.com")
    response = make_response(status_code=404, payload={"detail": "not found"})

    with mock.patch.object(client.session, "request", return_value=response):
        with pytest.raises(ApiError) as excinfo:
            client.get("/missing")

    assert excinfo.value.status_code == 404


def test_no_content_returns_none():
    client = RestClient("https://api.example.com")
    response = make_response(status_code=204, content=b"")

    with mock.patch.object(client.session, "request", return_value=response):
        assert client.get("/thing") is None


def test_absolute_url_is_not_prefixed():
    client = RestClient("https://api.example.com")
    assert client._url("https://other.example.org/v1") == "https://other.example.org/v1"


def test_parse_params():
    assert parse_params(["a=1", "b=two"]) == {"a": "1", "b": "two"}


def test_parse_params_rejects_bad_pair():
    with pytest.raises(ValueError):
        parse_params(["broken"])


def test_cli_outputs_json(capsys):
    client = RestClient("https://api.example.com")
    response = make_response(payload={"ok": True})

    with mock.patch("rest_fetch.cli.RestClient") as factory:
        factory.return_value = client
        with mock.patch.object(client.session, "request", return_value=response):
            code = main(["https://api.example.com/health"])

    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"ok": True}


def test_cli_reports_api_error(capsys):
    with mock.patch("rest_fetch.cli.RestClient") as factory:
        client = factory.return_value
        client.get.side_effect = ApiError("boom", status_code=500)
        code = main(["https://api.example.com/health"])

    assert code == 1
    assert "boom" in capsys.readouterr().err
