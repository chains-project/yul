from __future__ import annotations

import pytest
import responses

from api_fetcher import ApiClient, ApiError


@responses.activate
def test_get_returns_json():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        json=[{"id": 1}],
        status=200,
    )

    client = ApiClient("https://api.example.com")
    assert client.get("/items") == [{"id": 1}]


@responses.activate
def test_sends_auth_and_query_params():
    responses.add(responses.GET, "https://api.example.com/items", json=[])

    with ApiClient("https://api.example.com", token="secret") as client:
        client.get("/items", params={"limit": "5"})

    request = responses.calls[0].request
    assert request.headers["Authorization"] == "Bearer secret"
    assert request.url == "https://api.example.com/items?limit=5"


@responses.activate
def test_non_ok_status_raises():
    responses.add(responses.GET, "https://api.example.com/missing", status=404)

    client = ApiClient("https://api.example.com")
    with pytest.raises(ApiError) as exc:
        client.get("/missing")
    assert exc.value.status_code == 404


@responses.activate
def test_empty_body_returns_none():
    responses.add(responses.GET, "https://api.example.com/empty", body="", status=204)

    client = ApiClient("https://api.example.com")
    assert client.get("/empty") is None
