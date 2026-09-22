from unittest import mock

import pytest
import requests

from api_client import ApiClient, ApiError, fetch_json


def make_response(status_code=200, json_data=None, text=""):
    response = mock.Mock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 400
    response.text = text
    response.json.return_value = json_data
    return response


def test_get_json_returns_parsed_payload():
    session = mock.Mock()
    session.request.return_value = make_response(json_data={"id": 1})
    client = ApiClient("https://api.example.com/", session=session)

    assert client.get_json("/items/1") == {"id": 1}
    session.request.assert_called_once_with(
        "GET",
        "https://api.example.com/items/1",
        timeout=10.0,
        params=None,
        headers=None,
    )


def test_error_status_raises_api_error():
    session = mock.Mock()
    session.request.return_value = make_response(status_code=404, text="not found")
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError) as excinfo:
        client.get("/missing")

    assert "404" in str(excinfo.value)


def test_connection_error_is_wrapped():
    session = mock.Mock()
    session.request.side_effect = requests.ConnectionError("boom")

    with pytest.raises(ApiError):
        ApiClient("https://api.example.com", session=session).get("/items")


def test_fetch_json_uses_supplied_session():
    session = mock.Mock()
    session.request.return_value = make_response(json_data=[1, 2, 3])

    assert fetch_json("https://api.example.com/items", session=session) == [1, 2, 3]


def test_cli_prints_json(capsys):
    from api_client.__main__ import main

    with mock.patch("api_client.__main__.fetch_json", return_value={"ok": True}):
        assert main(["https://api.example.com/ping"]) == 0

    assert '"ok": true' in capsys.readouterr().out
