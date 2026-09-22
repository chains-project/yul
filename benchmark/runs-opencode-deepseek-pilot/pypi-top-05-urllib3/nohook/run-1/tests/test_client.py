import json
import unittest
from unittest import mock

from http_pool.client import DEFAULT_RETRY, HTTPError, HttpClient


def _response(status=200, body=b"{}"):
    response = mock.Mock()
    response.status = status
    response.data = body
    response.json.side_effect = lambda: json.loads(body.decode())
    return response


class RetryPolicyTests(unittest.TestCase):
    def test_default_retry_is_configured(self):
        self.assertEqual(DEFAULT_RETRY.total, 3)
        self.assertEqual(DEFAULT_RETRY.backoff_factor, 0.5)
        self.assertIn(503, DEFAULT_RETRY.status_forcelist)
        self.assertIn("GET", DEFAULT_RETRY.allowed_methods)
        self.assertNotIn("POST", DEFAULT_RETRY.allowed_methods)
        self.assertTrue(DEFAULT_RETRY.respect_retry_after_header)


class HttpClientTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("http_pool.client.PoolManager")
        self.addCleanup(patcher.stop)
        self.pool_cls = patcher.start()
        self.pool = self.pool_cls.return_value

    def test_pool_configured_for_connection_reuse(self):
        HttpClient(pool_connections=5, pool_maxsize=7, block=True)
        _, kwargs = self.pool_cls.call_args
        self.assertEqual(kwargs["num_pools"], 5)
        self.assertEqual(kwargs["maxsize"], 7)
        self.assertTrue(kwargs["block"])
        self.assertIs(kwargs["retries"], DEFAULT_RETRY)

    def test_request_returns_successful_response(self):
        self.pool.request.return_value = _response(200)
        with HttpClient() as client:
            response = client.request("GET", "https://example.com")
        self.assertEqual(response.status, 200)
        _, kwargs = self.pool.request.call_args
        self.assertEqual(kwargs["timeout"], 10.0)

    def test_request_raises_on_error_status(self):
        self.pool.request.return_value = _response(503)
        with HttpClient() as client:
            with self.assertRaises(HTTPError) as ctx:
                client.request("GET", "https://example.com")
        self.assertEqual(ctx.exception.status, 503)

    def test_request_wraps_transport_errors(self):
        import urllib3

        self.pool.request.side_effect = urllib3.exceptions.MaxRetryError(
            self.pool, "https://example.com"
        )
        with HttpClient() as client:
            with self.assertRaises(HTTPError):
                client.request("GET", "https://example.com")

    def test_get_json_decodes_body(self):
        self.pool.request.return_value = _response(200, b'{"ok": true}')
        with HttpClient() as client:
            self.assertEqual(client.get_json("https://example.com"), {"ok": True})

    def test_get_json_rejects_invalid_body(self):
        self.pool.request.return_value = _response(200, b"not json")
        with HttpClient() as client:
            with self.assertRaises(HTTPError):
                client.get_json("https://example.com")

    def test_close_clears_pool(self):
        client = HttpClient()
        client.close()
        self.pool.clear.assert_called_once()

    def test_per_request_overrides(self):
        self.pool.request.return_value = _response(200)
        with HttpClient() as client:
            client.request(
                "POST",
                "https://example.com",
                body="payload",
                timeout=3.5,
                retries=0,
            )
        _, kwargs = self.pool.request.call_args
        self.assertEqual(kwargs["body"], "payload")
        self.assertEqual(kwargs["timeout"], 3.5)
        self.assertEqual(kwargs["retries"], 0)


if __name__ == "__main__":
    unittest.main()
