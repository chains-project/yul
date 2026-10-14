import httpx
import pytest
import respx

from api_fetcher.client import ApiClient

BASE = "https://api.example.com"


@respx.mock
def test_get_returns_json():
    respx.get(f"{BASE}/items", params={"limit": "2"}).mock(
        return_value=httpx.Response(200, json=[{"id": 1}, {"id": 2}])
    )
    with ApiClient(BASE) as client:
        assert client.get("/items", params={"limit": 2}) == [{"id": 1}, {"id": 2}]


@respx.mock
def test_sends_bearer_token():
    route = respx.get(f"{BASE}/me").mock(return_value=httpx.Response(200, json={}))
    with ApiClient(BASE, token="secret") as client:
        client.get("/me")
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_raises_on_error_status():
    respx.get(f"{BASE}/missing").mock(return_value=httpx.Response(404))
    with ApiClient(BASE) as client, pytest.raises(httpx.HTTPStatusError):
        client.get("/missing")
