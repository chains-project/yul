"""Tests for :mod:`rest_client.client`."""

import pytest
import requests

from rest_client import ApiError, RestClient


class DummyResponse:
    def __init__(self, payload=None, status=200, json_error=False):
        self._payload = payload
        self.status_code = status
        self._json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        if self._json_error:
            raise ValueError("not json")
        return self._payload


class DummySession:
    def __init__(self, response):
        self._response = response
        self.headers = {}
        self.last = None
        self.closed = False

    def get(self, url, **kwargs):
        self.last = {"url": url, **kwargs}
        return self._response

    def close(self):
        self.closed = True


def test_base_url_trailing_slash_stripped():
    client = RestClient("https://api.example.com/", session=DummySession(None))
    assert client.base_url == "https://api.example.com"


def test_empty_base_url_rejected():
    with pytest.raises(ValueError):
        RestClient("", session=DummySession(None))


def test_get_returns_json():
    session = DummySession(DummyResponse({"id": 1}))
    client = RestClient("https://api.example.com", session=session)

    result = client.get("/users/1", params={"a": "b"})

    assert result == {"id": 1}
    assert session.last["url"] == "https://api.example.com/users/1"
    assert session.last["params"] == {"a": "b"}


def test_get_raises_api_error_on_http_error():
    session = DummySession(DummyResponse(status=404))
    client = RestClient("https://api.example.com", session=session)

    with pytest.raises(ApiError):
        client.get("/missing")


def test_get_raises_api_error_on_non_json():
    session = DummySession(DummyResponse(json_error=True))
    client = RestClient("https://api.example.com", session=session)

    with pytest.raises(ApiError):
        client.get("/text")


def test_context_manager_closes_session():
    session = DummySession(DummyResponse({}))
    with RestClient("https://api.example.com", session=session):
        pass
    assert session.closed
