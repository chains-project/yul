import json

import pytest
import requests

from api_fetcher.client import ApiError, fetch_json


class FakeResponse(object):
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.ok = 200 <= status_code < 400

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON object could be decoded")
        return self._payload


class FakeSession(object):
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.exc is not None:
            raise self.exc
        return self.response


def test_fetch_json_returns_parsed_payload():
    payload = {"items": [1, 2, 3]}
    session = FakeSession(response=FakeResponse(payload=payload))

    result = fetch_json("https://api.example.com/items", session=session)

    assert result == payload
    url, kwargs = session.calls[0]
    assert url == "https://api.example.com/items"
    assert kwargs["headers"]["Accept"] == "application/json"
    assert kwargs["timeout"] == 10.0


def test_fetch_json_forwards_params_and_headers():
    session = FakeSession(response=FakeResponse(payload={}))

    fetch_json(
        "https://api.example.com/search",
        params={"q": "python"},
        headers={"Authorization": "Bearer token"},
        timeout=2.5,
        session=session,
    )

    _, kwargs = session.calls[0]
    assert kwargs["params"] == {"q": "python"}
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    assert kwargs["timeout"] == 2.5


def test_fetch_json_raises_on_error_status():
    session = FakeSession(response=FakeResponse(status_code=404, payload={}))

    with pytest.raises(ApiError) as excinfo:
        fetch_json("https://api.example.com/missing", session=session)

    assert excinfo.value.status_code == 404


def test_fetch_json_raises_on_request_exception():
    session = FakeSession(exc=requests.ConnectionError("boom"))

    with pytest.raises(ApiError):
        fetch_json("https://api.example.com/down", session=session)


def test_fetch_json_raises_on_invalid_json():
    session = FakeSession(response=FakeResponse(status_code=200, payload=None))

    with pytest.raises(ApiError):
        fetch_json("https://api.example.com/html", session=session)
