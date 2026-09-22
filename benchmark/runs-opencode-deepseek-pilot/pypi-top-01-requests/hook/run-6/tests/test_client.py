from api_fetcher.client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        return self.response

    def close(self):
        pass


def test_get_returns_json():
    session = FakeSession(FakeResponse({"ok": True}))
    client = ApiClient("https://example.com/api", session=session)

    assert client.get("users", params={"page": 1}) == {"ok": True}
    assert session.calls[0][0] == "https://example.com/api/users"
    assert session.calls[0][1] == {"page": 1}


def test_get_raises_on_error_status():
    session = FakeSession(FakeResponse({"error": "nope"}, status_code=404))
    client = ApiClient("https://example.com/api", session=session)

    try:
        client.get("missing")
    except ApiError as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("ApiError was not raised")


def test_full_url_is_used_as_is():
    session = FakeSession(FakeResponse([]))
    client = ApiClient("https://example.com/api", session=session)

    client.get("https://other.example/items")
    assert session.calls[0][0] == "https://other.example/items"
