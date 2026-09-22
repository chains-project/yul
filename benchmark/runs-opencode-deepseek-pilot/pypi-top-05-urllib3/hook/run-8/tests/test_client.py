from http_client import HttpClient, build_client


def test_build_client_configures_pooling_and_retries():
    client = build_client(max_connections=7, max_retries=4, backoff_factor=0.25)
    retries = client.pool.connection_pool_kw["retries"]

    assert retries.total == 4
    assert retries.backoff_factor == 0.25
    assert "GET" in retries.allowed_methods
    assert client.pool.connection_pool_kw["maxsize"] == 7
    assert client.timeout.connect_timeout == 5.0
    assert client.timeout.read_timeout == 30.0

    client.close()


class _FakeResponse:
    status = 200
    data = b"ok"


class _FakePool:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return _FakeResponse()

    def clear(self):
        self.calls.clear()


def test_request_forwards_options_to_pool():
    pool = _FakePool()
    client = HttpClient(pool=pool, timeout=build_client().timeout)

    response = client.get("https://example.test/", headers={"X-Test": "1"})

    assert response.status == 200
    method, url, kwargs = pool.calls[0]
    assert (method, url) == ("GET", "https://example.test/")
    assert kwargs["headers"] == {"X-Test": "1"}
    assert kwargs["timeout"] is client.timeout
