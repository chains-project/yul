from unittest.mock import Mock

import pytest
import requests

from api_fetcher.client import ApiClient, ApiError


def _response(payload, status_code=200):
    response = Mock()
    response.status_code = status_code
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError()
    else:
        response.raise_for_status.return_value = None
        response.json.return_value = payload
    return response


def test_get_decodes_json_and_joins_url():
    session = Mock()
    session.get.return_value = _response({"ok": True})

    with ApiClient("https://api.example.com/", session=session) as client:
        result = client.get("users", params={"limit": 10})

    assert result == {"ok": True}
    session.get.assert_called_once_with(
        "https://api.example.com/users", params={"limit": 10}, timeout=10.0
    )


def test_get_without_path_uses_base_url():
    session = Mock()
    session.get.return_value = _response([1, 2, 3])

    client = ApiClient("https://api.example.com", session=session)
    assert client.get() == [1, 2, 3]
    session.get.assert_called_once_with(
        "https://api.example.com", params=None, timeout=10.0
    )


def test_http_error_raises_api_error():
    session = Mock()
    session.get.return_value = _response({}, status_code=404)

    with ApiClient("https://api.example.com", session=session) as client:
        with pytest.raises(ApiError, match="404"):
            client.get("missing")


def test_connection_error_raises_api_error():
    session = Mock()
    session.get.side_effect = requests.ConnectionError("boom")

    with ApiClient("https://api.example.com", session=session) as client:
        with pytest.raises(ApiError, match="failed"):
            client.get("users")


def test_invalid_json_raises_api_error():
    session = Mock()
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("not json")
    session.get.return_value = response

    with ApiClient("https://api.example.com", session=session) as client:
        with pytest.raises(ApiError, match="valid JSON"):
            client.get("page")


def test_headers_are_applied_to_session():
    session = Mock()
    session.headers = {}
    ApiClient("https://api.example.com", headers={"X-Api-Key": "secret"}, session=session)
    assert session.headers == {"X-Api-Key": "secret"}
