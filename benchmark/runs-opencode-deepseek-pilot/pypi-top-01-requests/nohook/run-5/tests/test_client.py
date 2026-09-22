import requests
import pytest

from api_fetcher.client import ApiError, fetch_json


class FakeResponse:
    def __init__(self, payload, error=None):
        self._payload = payload
        self._error = error

    def raise_for_status(self):
        if self._error is not None:
            raise self._error

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params, headers, timeout))
        return self.response


def test_fetch_json_returns_decoded_payload():
    session = FakeSession(FakeResponse({"ok": True}))
    assert fetch_json("https://example.test/data", session=session) == {"ok": True}


def test_fetch_json_passes_request_options():
    session = FakeSession(FakeResponse([]))
    fetch_json(
        "https://example.test/data",
        params={"page": "2"},
        headers={"Accept": "application/json"},
        timeout=5.0,
        session=session,
    )
    assert session.calls == [
        (
            "https://example.test/data",
            {"page": "2"},
            {"Accept": "application/json"},
            5.0,
        )
    ]


def test_fetch_json_wraps_request_errors():
    session = FakeSession(FakeResponse(None, requests.HTTPError("boom")))
    with pytest.raises(ApiError):
        fetch_json("https://example.test/data", session=session)
