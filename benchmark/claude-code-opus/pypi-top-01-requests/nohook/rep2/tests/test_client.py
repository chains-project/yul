import pytest
import responses

from api_fetcher import ApiClient, ApiError
from api_fetcher.cli import main

BASE = "https://api.example.com"


@responses.activate
def test_get_returns_json():
    responses.get(f"{BASE}/items", json=[{"id": 1}])
    with ApiClient(BASE) as client:
        assert client.get("/items") == [{"id": 1}]


@responses.activate
def test_get_sends_token_and_params():
    responses.get(
        f"{BASE}/items",
        json={},
        match=[responses.matchers.query_param_matcher({"page": "2"})],
    )
    with ApiClient(BASE, token="secret") as client:
        client.get("items", params={"page": "2"})
    assert responses.calls[0].request.headers["Authorization"] == "Bearer secret"


@responses.activate
def test_http_error_raises_api_error():
    responses.get(f"{BASE}/missing", status=404)
    with ApiClient(BASE, retries=0) as client, pytest.raises(ApiError):
        client.get("/missing")


@responses.activate
def test_cli_prints_json(capsys):
    responses.get(f"{BASE}/items/1", json={"id": 1})
    assert main(["--base-url", BASE, "/items/1"]) == 0
    assert '"id": 1' in capsys.readouterr().out
