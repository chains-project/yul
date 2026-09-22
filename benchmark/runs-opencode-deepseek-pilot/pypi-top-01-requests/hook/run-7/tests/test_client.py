import json

import pytest
import responses

from rest_fetcher import ApiError, RestClient, fetch


@responses.activate
def test_fetch_returns_json():
    responses.add(
        responses.GET,
        "https://api.example.com/items",
        json={"items": [1, 2, 3]},
        status=200,
    )

    assert fetch("https://api.example.com/items") == {"items": [1, 2, 3]}


@responses.activate
def test_client_sends_params_and_headers():
    responses.add(
        responses.GET,
        "https://api.example.com/search",
        json={"ok": True},
        status=200,
    )

    with RestClient(base_url="https://api.example.com") as client:
        data = client.get(
            "/search",
            params={"q": "python"},
            headers={"X-Token": "secret"},
        )

    assert data == {"ok": True}
    request = responses.calls[0].request
    assert "q=python" in request.url
    assert request.headers["X-Token"] == "secret"
    assert request.headers["Accept"] == "application/json"


@responses.activate
def test_http_error_raises_api_error():
    responses.add(
        responses.GET,
        "https://api.example.com/missing",
        json={"error": "not found"},
        status=404,
    )

    with pytest.raises(ApiError) as excinfo:
        fetch("https://api.example.com/missing")

    assert excinfo.value.status_code == 404


@responses.activate
def test_non_json_body_raises_api_error():
    responses.add(
        responses.GET,
        "https://api.example.com/html",
        body="<html></html>",
        status=200,
        content_type="text/html",
    )

    with pytest.raises(ApiError):
        fetch("https://api.example.com/html")


@responses.activate
def test_cli_prints_json(capsys):
    from rest_fetcher.cli import main

    responses.add(
        responses.GET,
        "https://api.example.com/ping",
        json={"pong": True},
        status=200,
    )

    assert main(["https://api.example.com/ping", "--compact"]) == 0
    out = capsys.readouterr().out.strip()
    assert json.loads(out) == {"pong": True}


@responses.activate
def test_cli_returns_error_code_on_failure(capsys):
    from rest_fetcher.cli import main

    responses.add(responses.GET, "https://api.example.com/boom", status=500)

    assert main(["https://api.example.com/boom"]) == 1
    assert "error:" in capsys.readouterr().err
