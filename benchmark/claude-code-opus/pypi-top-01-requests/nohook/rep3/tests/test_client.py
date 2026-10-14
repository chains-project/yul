import httpx
import pytest
import respx

from api_fetcher import ApiClient, ApiError
from api_fetcher.cli import main

BASE = "https://api.example.com"


@respx.mock
def test_get_returns_json():
    route = respx.get(f"{BASE}/items", params={"page": "2"}).mock(
        return_value=httpx.Response(200, json=[{"id": 1}])
    )
    with ApiClient(BASE, token="secret") as client:
        assert client.get("/items", params={"page": 2}) == [{"id": 1}]
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_http_error_raises_api_error():
    respx.get(f"{BASE}/missing").mock(return_value=httpx.Response(404, text="not found"))
    with ApiClient(BASE) as client, pytest.raises(ApiError, match="404"):
        client.get("/missing")


@respx.mock
def test_invalid_json_raises_api_error():
    respx.get(f"{BASE}/html").mock(return_value=httpx.Response(200, text="<html>"))
    with ApiClient(BASE) as client, pytest.raises(ApiError, match="not valid JSON"):
        client.get("/html")


@respx.mock
def test_cli_prints_json(capsys):
    respx.get(f"{BASE}/users/1").mock(return_value=httpx.Response(200, json={"name": "Ada"}))
    assert main(["--base-url", BASE, "/users/1"]) == 0
    assert '"name": "Ada"' in capsys.readouterr().out


@respx.mock
def test_cli_returns_1_on_error():
    respx.get(f"{BASE}/boom").mock(return_value=httpx.Response(500))
    assert main(["--base-url", BASE, "/boom"]) == 1
