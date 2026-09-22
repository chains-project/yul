import pytest
import responses

from rest_fetcher import ApiClient, FetchError

BASE_URL = "https://api.example.com/v1"


@responses.activate
def test_get_returns_decoded_json():
    responses.add(
        responses.GET,
        BASE_URL + "/items",
        json={"items": [1, 2, 3]},
        status=200,
    )

    with ApiClient(BASE_URL) as client:
        data = client.get("/items")

    assert data == {"items": [1, 2, 3]}
    assert responses.calls[0].request.headers["Accept"] == "application/json"


@responses.activate
def test_get_passes_query_params():
    responses.add(
        responses.GET,
        BASE_URL + "/search",
        json={"ok": True},
        status=200,
    )

    with ApiClient(BASE_URL) as client:
        client.get("/search", params={"q": "python"})

    assert "q=python" in responses.calls[0].request.url


@responses.activate
def test_http_error_raises_fetch_error():
    responses.add(responses.GET, BASE_URL + "/missing", status=404)

    with ApiClient(BASE_URL) as client:
        with pytest.raises(FetchError):
            client.get("/missing")


@responses.activate
def test_invalid_json_raises_fetch_error():
    responses.add(
        responses.GET,
        BASE_URL + "/bad",
        body="not json",
        status=200,
        content_type="text/plain",
    )

    with ApiClient(BASE_URL) as client:
        with pytest.raises(FetchError):
            client.get("/bad")


def test_url_join_handles_slashes():
    client = ApiClient(BASE_URL + "/")
    try:
        assert client._url("items") == BASE_URL + "/items"
        assert client._url("/items") == BASE_URL + "/items"
        assert client._url("http://other.test/x") == "http://other.test/x"
    finally:
        client.close()
