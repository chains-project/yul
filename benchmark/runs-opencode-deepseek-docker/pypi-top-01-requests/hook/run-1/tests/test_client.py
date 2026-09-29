import pytest
import requests

from api_fetcher import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}", response=self)


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response

    def close(self):
        self.closed = True


def test_get_joins_base_url_and_path():
    session = FakeSession(FakeResponse({"ok": True}))
    client = ApiClient("https://api.example.com/", timeout=5, session=session)

    assert client.get("/v1/items", params={"q": "x"}) == {"ok": True}
    assert session.calls == [
        {
            "url": "https://api.example.com/v1/items",
            "params": {"q": "x"},
            "timeout": 5,
        }
    ]


def test_get_accepts_absolute_url_without_base():
    session = FakeSession(FakeResponse([1, 2]))
    client = ApiClient(session=session)

    assert client.get("https://other.test/data") == [1, 2]
    assert session.calls[0]["url"] == "https://other.test/data"


def test_relative_path_without_base_url_raises():
    client = ApiClient(session=FakeSession(FakeResponse()))
    with pytest.raises(ValueError):
        client.get("/v1/items")


def test_http_error_is_wrapped_in_api_error():
    session = FakeSession(FakeResponse(status_code=500))
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError):
        client.get("/boom")
