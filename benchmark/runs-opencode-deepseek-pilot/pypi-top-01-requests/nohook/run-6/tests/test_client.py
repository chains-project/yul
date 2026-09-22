"""Tests for :mod:`api_fetch.client`."""

from __future__ import annotations

import pytest
import responses

from api_fetch import ApiError, fetch_json


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
def test_fetch_json_sends_params_and_headers():
    responses.add(
        responses.GET,
        "https://api.example.com/search",
        json={"ok": True},
        status=200,
    )

    fetch_json(
        "https://api.example.com/search",
        params={"q": "python"},
        headers={"X-Token": "secret"},
    )

    request = responses.calls[0].request
    assert "q=python" in request.url
    assert request.headers["X-Token"] == "secret"


@responses.activate
def test_fetch_json_raises_on_http_error():
    responses.add(responses.GET, "https://api.example.com/missing", status=404)

    with pytest.raises(ApiError, match="404"):
        fetch_json("https://api.example.com/missing")


@responses.activate
def test_fetch_json_raises_on_invalid_json():
    responses.add(
        responses.GET,
        "https://api.example.com/bad",
        body="not json",
        status=200,
    )

    with pytest.raises(ApiError, match="valid JSON"):
        fetch_json("https://api.example.com/bad")
