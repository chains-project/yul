import httpx
import pytest

from api_fetcher import ApiClient, ApiError


def make_client(handler) -> ApiClient:
    transport = httpx.MockTransport(handler)
    return ApiClient("https://api.example.com", token="secret", transport=transport)


def test_get_returns_json_and_sends_auth():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/items"
        assert request.url.params["limit"] == "5"
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(200, json=[{"id": 1}])

    with make_client(handler) as client:
        assert client.get("/items", params={"limit": 5}) == [{"id": 1}]


def test_http_error_raises_api_error():
    with make_client(lambda r: httpx.Response(404)) as client:
        with pytest.raises(ApiError, match="404"):
            client.get("/missing")


def test_invalid_json_raises_api_error():
    with make_client(lambda r: httpx.Response(200, text="not json")) as client:
        with pytest.raises(ApiError, match="not valid JSON"):
            client.get("/bad")


def test_network_error_raises_api_error():
    def handler(request):
        raise httpx.ConnectError("boom", request=request)

    with make_client(handler) as client:
        with pytest.raises(ApiError, match="failed"):
            client.get("/down")
