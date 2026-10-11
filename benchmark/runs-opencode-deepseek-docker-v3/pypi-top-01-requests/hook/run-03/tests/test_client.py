import httpx
import pytest

from api_fetcher.client import ApiError, RestClient


def make_client(handler):
    transport = httpx.MockTransport(handler)
    return RestClient(
        client=httpx.Client(base_url="https://api.example.com", transport=transport)
    )


def test_get_returns_decoded_json():
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/items"
        assert request.url.params["page"] == "2"
        return httpx.Response(200, json={"items": [1, 2, 3]})

    with make_client(handler) as client:
        assert client.get("/items", params={"page": 2}) == {"items": [1, 2, 3]}


def test_get_raises_api_error_on_http_error():
    def handler(request):
        return httpx.Response(500, json={"error": "boom"})

    with make_client(handler) as client:
        with pytest.raises(ApiError, match="HTTP 500"):
            client.get("/items")


def test_get_raises_api_error_on_transport_error():
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    with make_client(handler) as client:
        with pytest.raises(ApiError, match="failed"):
            client.get("/items")


def test_get_raises_api_error_on_invalid_json():
    def handler(request):
        return httpx.Response(200, text="not json")

    with make_client(handler) as client:
        with pytest.raises(ApiError, match="valid JSON"):
            client.get("/items")
