import pytest
import requests

from api_fetcher.client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload=None, status_code=200, error=None):
        self._payload = payload
        self.status_code = status_code
        self._error = error

    def raise_for_status(self):
        if self._error is not None:
            raise self._error

    def json(self):
        if self._payload is _INVALID_JSON:
            raise ValueError("no json")
        return self._payload


_INVALID_JSON = object()


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.calls = []
        self.closed = False

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def close(self):
        self.closed = True


def test_get_joins_base_url_and_parses_json():
    session = FakeSession(FakeResponse({"ok": True}))
    client = ApiClient("https://api.example.com/v1", session=session)

    result = client.get("users", params={"page": 2})

    assert result == {"ok": True}
    assert session.calls[0]["url"] == "https://api.example.com/v1/users"
    assert session.calls[0]["params"] == {"page": 2}


def test_get_uses_absolute_url_as_is():
    session = FakeSession(FakeResponse([]))
    client = ApiClient("https://api.example.com", session=session)

    client.get("http://other.example.com/items")

    assert session.calls[0]["url"] == "http://other.example.com/items"


def test_get_wraps_request_errors():
    session = FakeSession(requests.ConnectionError("boom"))
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError, match="failed"):
        client.get("users")


def test_get_wraps_http_error_status():
    error = requests.HTTPError("404 Client Error")
    session = FakeSession(FakeResponse(status_code=404, error=error))
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError):
        client.get("missing")


def test_get_wraps_invalid_json():
    session = FakeSession(FakeResponse(_INVALID_JSON))
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError, match="invalid JSON"):
        client.get("broken")


def test_context_manager_closes_session():
    session = FakeSession(FakeResponse({}))
    with ApiClient("https://api.example.com", session=session) as client:
        assert isinstance(client, ApiClient)

    assert session.closed is True
