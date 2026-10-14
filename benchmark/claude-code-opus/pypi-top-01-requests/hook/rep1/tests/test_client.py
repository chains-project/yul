import httpx
import pytest
import respx

from api_fetcher.client import ApiClient
from api_fetcher.main import main

BASE = "https://api.example.com"


@respx.mock
def test_get_returns_json():
    route = respx.get(f"{BASE}/items").mock(return_value=httpx.Response(200, json=[{"id": 1}]))
    with ApiClient(BASE, token="secret") as client:
        assert client.get("/items") == [{"id": 1}]
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_get_raises_on_error_status():
    respx.get(f"{BASE}/missing").mock(return_value=httpx.Response(404))
    with ApiClient(BASE) as client, pytest.raises(httpx.HTTPStatusError):
        client.get("/missing")


@respx.mock
def test_main_prints_json(capsys):
    respx.get(f"{BASE}/items").mock(return_value=httpx.Response(200, json={"ok": True}))
    assert main(["/items", "--base-url", BASE]) == 0
    assert '"ok": true' in capsys.readouterr().out


def test_main_requires_base_url(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    assert main(["/items"]) == 2
