"""Tests for the REST API fetch client."""

import pytest
import responses

from rest_fetcher import ApiError, fetch_json


@responses.activate
def test_fetch_json_returns_decoded_body():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        json={"items": [1, 2, 3]},
        status=200,
    )

    assert fetch_json("https://api.example.com/items") == {"items": [1, 2, 3]}


@responses.activate
def test_fetch_json_sends_query_params_and_headers():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        json=[],
        status=200,
    )

    fetch_json(
        "https://api.example.com/items",
        params={"limit": "10"},
        headers={"Authorization": "Bearer token"},
    )

    request = responses.calls[0].request
    assert "limit=10" in request.url
    assert request.headers["Authorization"] == "Bearer token"


@responses.activate
def test_fetch_json_raises_on_error_status():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        status=500,
    )

    with pytest.raises(ApiError) as excinfo:
        fetch_json("https://api.example.com/items")

    assert excinfo.value.status_code == 500


@responses.activate
def test_fetch_json_raises_on_invalid_json():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        body="not json",
        status=200,
        content_type="text/plain",
    )

    with pytest.raises(ApiError):
        fetch_json("https://api.example.com/items")
