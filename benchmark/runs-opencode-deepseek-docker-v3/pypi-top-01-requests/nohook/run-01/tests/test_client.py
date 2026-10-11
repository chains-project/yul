import httpx
import pytest

from api_fetcher import ApiError, fetch_json


def test_fetch_json_returns_decoded_body():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    data = fetch_json(
        "https://example.test/data",
        transport=httpx.MockTransport(handler),
    )

    assert data == {"ok": True}


def test_fetch_json_raises_on_client_error_without_retrying():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(404)

    with pytest.raises(ApiError):
        fetch_json(
            "https://example.test/missing",
            transport=httpx.MockTransport(handler),
        )

    assert calls == 1


def test_fetch_json_retries_server_errors():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500)

    with pytest.raises(ApiError):
        fetch_json(
            "https://example.test/flaky",
            retries=3,
            transport=httpx.MockTransport(handler),
        )

    assert calls == 3
