import pytest

from api_fetcher.cli import main, parse_headers


def test_parse_headers():
    assert parse_headers(["Authorization: Bearer token", "X-A: 1"]) == {
        "Authorization": "Bearer token",
        "X-A": "1",
    }


def test_parse_headers_rejects_missing_colon():
    with pytest.raises(ValueError):
        parse_headers(["nope"])


def test_main_prints_error_for_bad_header(capsys):
    exit_code = main(["--header", "nope", "https://api.example.com"])
    assert exit_code == 2
    assert "invalid header" in capsys.readouterr().err
