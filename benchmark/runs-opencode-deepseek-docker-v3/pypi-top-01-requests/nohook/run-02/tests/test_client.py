import httpx
import pytest
import respx

from api_fetcher import ApiError, fetch


@respx.mock
def test_fetch_returns_decoded_json() -> None:
    respx.get("https://api.example.com/users").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Ada"})
    )
    response = fetch("https://api.example.com/users")
    assert response.status_code == 200
    assert response.data == {"id": 1, "name": "Ada"}


@respx.mock
def test_fetch_sends_params_and_headers() -> None:
    route = respx.get("https://api.example.com/search").mock(
        return_value=httpx.Response(200, json=[])
    )
    fetch(
        "https://api.example.com/search",
        params={"q": "python"},
        headers={"Authorization": "Bearer token"},
    )
    request = route.calls.last.request
    assert request.url.params["q"] == "python"
    assert request.headers["authorization"] == "Bearer token"


@respx.mock
def test_fetch_raises_api_error_on_error_status() -> None:
    respx.get("https://api.example.com/missing").mock(
        return_value=httpx.Response(404, json={"error": "not found"})
    )
    with pytest.raises(ApiError) as excinfo:
        fetch("https://api.example.com/missing")
    assert excinfo.value.status_code == 404


@respx.mock
def test_fetch_raises_api_error_on_invalid_json() -> None:
    respx.get("https://api.example.com/bad").mock(
        return_value=httpx.Response(200, text="not json")
    )
    with pytest.raises(ApiError):
        fetch("https://api.example.com/bad")


@respx.mock
def test_fetch_wraps_connection_errors() -> None:
    respx.get("https://api.example.com/down").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    with pytest.raises(ApiError):
        fetch("https://api.example.com/down")
