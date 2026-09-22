from rest_fetcher.cli import build_parser, _parse_pairs
from rest_fetcher.client import RestClient


def test_parse_pairs():
    assert _parse_pairs(["a=1", "b=two"]) == {"a": "1", "b": "two"}


def test_base_url_trailing_slash():
    client = RestClient("https://example.com/")
    assert client.base_url == "https://example.com"
    client.close()


def test_get_builds_url(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        return FakeResponse()

    client = RestClient("https://example.com/api")
    monkeypatch.setattr(client.session, "get", fake_get)

    result = client.get("/users", params={"page": 1})

    assert result == {"ok": True}
    assert captured["url"] == "https://example.com/api/users"
    assert captured["params"] == {"page": 1}
    client.close()


def test_cli_parser_requires_url():
    parser = build_parser()
    args = parser.parse_args(["https://example.com"])
    assert args.url == "https://example.com"
