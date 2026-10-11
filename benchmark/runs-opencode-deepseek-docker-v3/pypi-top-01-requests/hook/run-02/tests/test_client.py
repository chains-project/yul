from __future__ import annotations

import httpx
import pytest

from rest_fetcher.client import ApiClient, ApiError


def make_client(handler, **kwargs) -> ApiClient:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.example.com")
    return ApiClient("https://api.example.com", client=http_client, **kwargs)


def test_get_returns_parsed_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users"
        return httpx.Response(200, json={"id": 1, "name": "Ada"})

    client = make_client(handler)
    assert client.get("/users") == {"id": 1, "name": "Ada"}


def test_get_passes_query_parameters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {"page": "2"}
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler)
    assert client.get("/items", page=2) == {"ok": True}


def test_http_error_raises_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "not found"})

    client = make_client(handler)
    with pytest.raises(ApiError) as excinfo:
        client.get("/missing")
    assert excinfo.value.status_code == 404


def test_invalid_json_raises_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    client = make_client(handler)
    with pytest.raises(ApiError):
        client.get("/plain")


def test_transport_error_raises_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = make_client(handler)
    with pytest.raises(ApiError):
        client.get("/down")


def test_context_manager_does_not_close_external_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    client = make_client(handler)
    with client:
        pass
    assert not client._client.is_closed
