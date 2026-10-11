import httpx
import pytest

from api_client.client import APIClient
from api_client.exceptions import APIError


def test_get_json_returns_decoded_body(httpx_mock):
    httpx_mock.add_response(
        url="https://api.example.com/users?page=1",
        json=[{"id": 1, "name": "Ada"}],
    )

    with APIClient("https://api.example.com") as client:
        data = client.get_json("/users", params={"page": 1})

    assert data == [{"id": 1, "name": "Ada"}]


def test_get_json_sends_bearer_token(httpx_mock):
    httpx_mock.add_response(json={})

    with APIClient("https://api.example.com", token="secret") as client:
        client.get_json("/me")

    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Bearer secret"


def test_get_json_raises_api_error_on_http_status(httpx_mock):
    httpx_mock.add_response(status_code=404, json={"detail": "not found"})

    with APIClient("https://api.example.com") as client:
        with pytest.raises(APIError) as exc_info:
            client.get_json("/missing")

    assert exc_info.value.status_code == 404


def test_get_json_raises_api_error_on_invalid_json(httpx_mock):
    httpx_mock.add_response(text="not json")

    with APIClient("https://api.example.com") as client:
        with pytest.raises(APIError):
            client.get_json("/broken")


def test_get_json_raises_api_error_on_connection_error(httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("boom"))

    with APIClient("https://api.example.com") as client:
        with pytest.raises(APIError):
            client.get_json("/down")
