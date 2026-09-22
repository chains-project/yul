import json

import pytest

from httpclient import HttpClient
from httpclient.client import build_retry


class FakeResponse(object):
    def __init__(self, status=200, data=b"{}"):
        self.status = status
        self.data = data


class FakePoolManager(object):
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.cleared = False
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        return FakeResponse(200, json.dumps({"ok": True}).encode("utf-8"))

    def clear(self):
        self.cleared = True


@pytest.fixture
def fake_pool(monkeypatch):
    created = {}

    def factory(**kwargs):
        pool = FakePoolManager(**kwargs)
        created["pool"] = pool
        return pool

    monkeypatch.setattr("httpclient.client.urllib3.PoolManager", factory)
    return created


def test_retry_policy_defaults():
    retry = build_retry(total=3, backoff_factor=0.5)
    assert retry.total == 3
    assert 503 in retry.status_forcelist
    assert "GET" in retry.allowed_methods


def test_pool_configured_with_retries(fake_pool):
    HttpClient(num_pools=7, maxsize=3, retries=4)
    kwargs = fake_pool["pool"].init_kwargs
    assert kwargs["num_pools"] == 7
    assert kwargs["maxsize"] == 3
    assert kwargs["retries"].total == 4


def test_get_json(fake_pool):
    client = HttpClient()
    assert client.get_json("https://example.test/get") == {"ok": True}


def test_error_raises(monkeypatch):
    client = HttpClient()
    monkeypatch.setattr(
        client._pool, "request", lambda *a, **k: FakeResponse(500, b"boom")
    )
    with pytest.raises(Exception):
        client.get("https://example.test/")


def test_close_clears_pool(fake_pool):
    client = HttpClient()
    client.close()
    assert fake_pool["pool"].cleared is True
