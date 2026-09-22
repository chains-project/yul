import pytest
import requests

from api_fetcher.client import ApiError, RestClient


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = {} if payload is None else payload
        self.ok = 200 <= status_code < 400

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses=None, error=None):
        self.headers = {}
        self.responses = list(responses or [])
        self.error = error
        self.calls = []
        self.closed = False
        self.mounted = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if self.error is not None:
            raise self.error
        if self.responses:
            return self.responses.pop(0)
        return FakeResponse()

    def mount(self, prefix, adapter):
        self.mounted.append(prefix)

    def close(self):
        self.closed = True


def make_client(session, **kwargs):
    return RestClient("https://api.example.com/", session=session, **kwargs)


def test_builds_url_from_base_and_path():
    session = FakeSession()
    with make_client(session) as client:
        client.get("/users")
    assert session.calls[0]["url"] == "https://api.example.com/users"


def test_absolute_url_bypasses_base():
    session = FakeSession()
    with make_client(session) as client:
        client.get("https://other.example.com/data")
    assert session.calls[0]["url"] == "https://other.example.com/data"


def test_passes_params_headers_and_timeout():
    session = FakeSession()
    with make_client(session, timeout=5.0) as client:
        client.get("users", params={"page": 2}, headers={"X-Token": "abc"})
    kwargs = session.calls[0]["kwargs"]
    assert kwargs["params"] == {"page": 2}
    assert kwargs["headers"] == {"X-Token": "abc"}
    assert kwargs["timeout"] == 5.0


def test_get_json_returns_payload():
    session = FakeSession([FakeResponse(payload={"id": 1})])
    with make_client(session) as client:
        assert client.get_json("users/1") == {"id": 1}


def test_non_ok_response_raises_api_error():
    session = FakeSession([FakeResponse(status_code=404)])
    with make_client(session) as client:
        with pytest.raises(ApiError) as excinfo:
            client.get("missing")
    assert excinfo.value.status_code == 404


def test_request_exception_is_wrapped():
    session = FakeSession(error=requests.ConnectionError("boom"))
    with make_client(session) as client:
        with pytest.raises(ApiError) as excinfo:
            client.get("users")
    assert excinfo.value.status_code is None


def test_context_manager_closes_session():
    session = FakeSession()
    with make_client(session):
        pass
    assert session.closed is True
