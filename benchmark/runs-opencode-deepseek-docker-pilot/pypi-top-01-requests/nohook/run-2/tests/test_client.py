import pytest
import requests

from api_fetcher.client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload=None, status_code=200, url="https://api.example.com/data"):
        self._payload = payload
        self.status_code = status_code
        self.url = url

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} error")
            error.response = self
            raise error


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


def make_client(response, **kwargs):
    session = FakeSession(response)
    client = ApiClient("https://api.example.com/", session=session, **kwargs)
    return client, session


def test_get_json_joins_relative_path():
    client, session = make_client(FakeResponse({"ok": True}))
    assert client.get_json("users") == {"ok": True}
    assert session.calls[0]["url"] == "https://api.example.com/users"


def test_get_keeps_absolute_url():
    client, session = make_client(FakeResponse({"ok": True}))
    client.get("https://other.example.com/things")
    assert session.calls[0]["url"] == "https://other.example.com/things"


def test_params_and_timeout_are_forwarded():
    client, session = make_client(FakeResponse({"ok": True}), timeout=2.5)
    client.get_json("search", params={"q": "python"})
    assert session.calls[0]["params"] == {"q": "python"}
    assert session.calls[0]["timeout"] == 2.5


def test_http_error_becomes_api_error():
    client, _ = make_client(FakeResponse(status_code=404))
    with pytest.raises(ApiError, match="404"):
        client.get("missing")


def test_connection_error_becomes_api_error():
    client, _ = make_client(requests.ConnectionError("boom"))
    with pytest.raises(ApiError, match="boom"):
        client.get("data")


def test_invalid_json_becomes_api_error():
    client, _ = make_client(FakeResponse(ValueError("no json")))
    with pytest.raises(ApiError, match="valid JSON"):
        client.get_json("data")


def test_relative_path_requires_base_url():
    client = ApiClient(session=FakeSession(FakeResponse()))
    with pytest.raises(ApiError, match="base_url"):
        client.get("data")


def test_headers_are_applied_to_session():
    session = FakeSession(FakeResponse())
    ApiClient("https://api.example.com", headers={"Authorization": "Bearer token"}, session=session)
    assert session.headers["Authorization"] == "Bearer token"


def test_context_manager_closes_session():
    client, session = make_client(FakeResponse())
    with client:
        pass
    assert session.closed is True
