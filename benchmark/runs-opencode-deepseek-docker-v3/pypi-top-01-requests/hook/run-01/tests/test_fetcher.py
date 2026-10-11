import httpx
import pytest

from api_fetcher import ApiError, fetch


def test_fetch_returns_json(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://api.test/users/1?active=true"
        assert request.headers["authorization"] == "Bearer secret"
        return httpx.Response(200, json={"id": 1})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        httpx, "get", lambda *a, **k: httpx.Client(transport=transport).get(*a, **k)
    )

    data = fetch(
        "/users/1",
        base_url="https://api.test",
        params={"active": "true"},
        token="secret",
    )
    assert data == {"id": 1}


def test_fetch_requires_base_url(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    with pytest.raises(ApiError):
        fetch("/users/1")


def test_fetch_raises_on_http_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "not found"})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        httpx, "get", lambda *a, **k: httpx.Client(transport=transport).get(*a, **k)
    )

    with pytest.raises(ApiError):
        fetch("https://api.test/missing")
