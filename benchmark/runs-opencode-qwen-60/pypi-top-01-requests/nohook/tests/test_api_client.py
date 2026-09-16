"""Tests for api_fetcher.api_client."""

from __future__ import annotations

import json as _json

import pytest
import responses


class TestAPIClientGet:
    @responses.activate
    def test_get_returns_json(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"items": [{"id": 1}]},
            status=200,
        )
        with APIClient("https://api.example.com") as client:
            result = client.get("/users")
        assert result == {"items": [{"id": 1}]}

    @responses.activate
    def test_get_raises_on_404(self):
        from api_fetcher.api_client import APIClient
        from requests.exceptions import HTTPError

        responses.add(
            responses.GET,
            "https://api.example.com/missing",
            json={"error": "not found"},
            status=404,
        )
        with APIClient("https://api.example.com") as client:
            with pytest.raises(HTTPError):
                client.get("/missing")

    @responses.activate
    def test_get_with_params(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"items": []},
            status=200,
        )
        with APIClient("https://api.example.com") as client:
            client.get("/users", params={"page": 2, "limit": 10})

        assert len(responses.calls) == 1
        assert "page=2" in responses.calls[0].request.url
        assert "limit=10" in responses.calls[0].request.url


class TestAPIClientPost:
    @responses.activate
    def test_post_sends_json_body(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 42, "name": "alice"},
            status=201,
        )
        with APIClient("https://api.example.com") as client:
            result = client.post("/users", json={"name": "alice"})
        assert result == {"id": 42, "name": "alice"}


class TestAPIClientGetAll:
    @responses.activate
    def test_get_all_paginates(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.GET,
            "https://api.example.com/items",
            json=[{"id": 1}, {"id": 2}],
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.example.com/items",
            json=[{"id": 3}],
            status=200,
        )
        with APIClient("https://api.example.com") as client:
            items = client.get_all("/items")
        assert len(items) == 3

    @responses.activate
    def test_get_all_stops_on_empty_page(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.GET,
            "https://api.example.com/items",
            json=[{"id": 1}],
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.example.com/items",
            json=[],
            status=200,
        )
        with APIClient("https://api.example.com") as client:
            items = client.get_all("/items")
        assert len(items) == 1
        assert len(responses.calls) == 2


class TestAPIClientContextManager:
    @responses.activate
    def test_context_manager_closes_session(self):
        from api_fetcher.api_client import APIClient

        responses.add(
            responses.GET,
            "https://api.example.com/data",
            json={},
            status=200,
        )
        with APIClient("https://api.example.com") as client:
            client.get("/data")
        assert client.session.adapters == {}