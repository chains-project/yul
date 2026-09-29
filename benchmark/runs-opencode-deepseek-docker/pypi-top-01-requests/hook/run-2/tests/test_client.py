from __future__ import annotations

import pytest
import responses

from api_fetch.client import ApiClient, ApiError


@responses.activate
def test_get_returns_parsed_json() -> None:
    responses.get("https://example.test/users", json=[{"id": 1}], status=200)

    client = ApiClient("https://example.test")

    assert client.get("/users") == [{"id": 1}]


@responses.activate
def test_get_strips_leading_slash_and_forwards_params() -> None:
    responses.get(
        "https://example.test/users",
        json=[],
        match=[responses.matchers.query_param_matcher({"page": "2"})],
    )

    client = ApiClient("https://example.test/")

    assert client.get("users", params={"page": "2"}) == []


@responses.activate
def test_http_error_raises_api_error() -> None:
    responses.get("https://example.test/missing", status=404)

    client = ApiClient("https://example.test")

    with pytest.raises(ApiError):
        client.get("/missing")
