import httpx
import pytest
import respx

from api_fetcher import ApiClient, ApiError
from api_fetcher.cli import main

BASE = "https://api.example.com"


@respx.mock
def test_get_returns_json():
    route = respx.get(f"{BASE}/items", params={"page": "2"}).respond(json=[{"id": 1}])
    with ApiClient(BASE) as client:
        assert client.get("/items", params={"page": 2}) == [{"id": 1}]
    assert route.called


@respx.mock
def test_sends_bearer_token():
    route = respx.get(f"{BASE}/me").respond(json={})
    with ApiClient(BASE, token="secret") as client:
        client.get("/me")
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_http_error_raises_api_error():
    respx.get(f"{BASE}/missing").respond(404, text="not found")
    with ApiClient(BASE) as client, pytest.raises(ApiError, match="404"):
        client.get("/missing")


@respx.mock
def test_connection_error_raises_api_error():
    respx.get(f"{BASE}/down").mock(side_effect=httpx.ConnectError("boom"))
    with ApiClient(BASE) as client, pytest.raises(ApiError, match="failed"):
        client.get("/down")


@respx.mock
def test_cli_prints_json(capsys):
    respx.get(f"{BASE}/items", params={"q": "x"}).respond(json={"ok": True})
    assert main(["--base-url", BASE, "/items", "-p", "q=x"]) == 0
    assert '"ok": true' in capsys.readouterr().out
