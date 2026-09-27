import pytest

from api_fetcher.client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        return self.response


def test_get_returns_parsed_json():
    session = FakeSession(FakeResponse({"id": 1}))
    client = ApiClient("https://api.example.com", session=session)

    assert client.get("/users/1") == {"id": 1}


def test_get_builds_url_and_params():
    session = FakeSession(FakeResponse([]))
    client = ApiClient("https://api.example.com/", session=session)

    client.get("users", params={"page": 2})

    url, params, timeout = session.calls[0]
    assert url == "https://api.example.com/users"
    assert params == {"page": 2}
    assert timeout == 10.0


def test_headers_are_applied():
    session = FakeSession(FakeResponse({}))
    ApiClient("https://api.example.com", session=session, headers={"Authorization": "token"})

    assert session.headers == {"Authorization": "token"}


def test_error_response_raises():
    session = FakeSession(FakeResponse({"error": "nope"}, status_code=404))
    client = ApiClient("https://api.example.com", session=session)

    with pytest.raises(ApiError):
        client.get("/missing")
