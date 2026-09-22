from unittest import mock

import pytest
import requests

from api_fetch.client import ApiClient, ApiError


def _response(status_code=200, payload=None, ok=True):
    response = mock.Mock(spec=requests.Response)
    response.status_code = status_code
    response.ok = ok
    response.json.return_value = payload
    return response


def test_get_returns_json():
    session = mock.Mock(spec=requests.Session)
    session.get.return_value = _response(payload={"id": 1})

    client = ApiClient("https://api.example.com/", session=session)
    assert client.get("/users/1") == {"id": 1}

    session.get.assert_called_once_with(
        "https://api.example.com/users/1", params=None, timeout=10.0
    )


def test_get_raises_on_http_error():
    session = mock.Mock(spec=requests.Session)
    session.get.return_value = _response(status_code=404, ok=False)

    client = ApiClient("https://api.example.com", session=session)
    with pytest.raises(ApiError):
        client.get("/missing")


def test_get_raises_on_connection_error():
    session = mock.Mock(spec=requests.Session)
    session.get.side_effect = requests.ConnectionError("boom")

    client = ApiClient("https://api.example.com", session=session)
    with pytest.raises(ApiError):
        client.get("/users")
