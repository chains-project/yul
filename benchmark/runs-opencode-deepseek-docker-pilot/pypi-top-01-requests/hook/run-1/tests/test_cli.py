import pytest

from api_fetcher.cli import parse_params


def test_parse_params():
    assert parse_params(["q=hello", "page=2"]) == {"q": "hello", "page": "2"}


def test_parse_params_rejects_malformed():
    with pytest.raises(ValueError):
        parse_params(["missing_equals"])
