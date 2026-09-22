import pytest

from api_fetcher import ApiClient, ApiError


class FakeResponse(object):
    def __init__(self, status_code=200, payload=None, content=True, url="https://api.example.com"):
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}" if content else b""
        self.url = url

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._payload


class FakeSession(object):
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.calls = []

    def request(self, method, url, params=None, json=None, **kwargs):
        self.calls.append(
            {"method": method, "url": url, "params": params, "json": json, "kwargs": kwargs}
        )
        return self.response

    def close(self):
        pass


def make_client(response):
    session = FakeSession(response)
    return ApiClient("https://api.example.com", session=session), session


def test_get_returns_json():
    client, session = make_client(FakeResponse(payload=[{"id": 1}]))
    assert client.get("/users") == [{"id": 1}]
    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"] == "https://api.example.com/users"


def test_query_params_are_passed():
    client, session = make_client(FakeResponse(payload={"ok": True}))
    client.get("/users", params={"page": 2})
    assert session.calls[0]["params"] == {"page": 2}


def test_timeout_default_is_applied():
    client, session = make_client(FakeResponse(payload={}))
    client.get("/users")
    assert session.calls[0]["kwargs"]["timeout"] == 10.0


def test_error_raises_api_error():
    client, _ = make_client(FakeResponse(status_code=404))
    with pytest.raises(ApiError) as excinfo:
        client.get("/users")
    assert excinfo.value.status_code == 404


def test_empty_body_returns_none():
    client, _ = make_client(FakeResponse(status_code=204, content=False))
    assert client.get("/users") is None


def test_base_url_trailing_slash_normalized():
    session = FakeSession(FakeResponse(payload={}))
    client = ApiClient("https://api.example.com/", session=session)
    client.get("users")
    assert session.calls[0]["url"] == "https://api.example.com/users"
