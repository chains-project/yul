import unittest
from unittest import mock

import requests

from rest_fetcher.client import APIError, fetch_json


class FetchJsonTests(unittest.TestCase):
    def test_returns_parsed_json(self):
        response = mock.Mock()
        response.json.return_value = {"ok": True}
        with mock.patch("rest_fetcher.client.requests.get", return_value=response) as get:
            data = fetch_json("https://example.test/api", params={"q": "x"})
        self.assertEqual(data, {"ok": True})
        get.assert_called_once_with(
            "https://example.test/api",
            params={"q": "x"},
            headers=None,
            timeout=10.0,
        )
        response.raise_for_status.assert_called_once()

    def test_wraps_http_errors(self):
        response = mock.Mock()
        response.raise_for_status.side_effect = requests.HTTPError("500")
        with mock.patch("rest_fetcher.client.requests.get", return_value=response):
            with self.assertRaises(APIError):
                fetch_json("https://example.test/api")

    def test_wraps_connection_errors(self):
        with mock.patch(
            "rest_fetcher.client.requests.get",
            side_effect=requests.ConnectionError("boom"),
        ):
            with self.assertRaises(APIError):
                fetch_json("https://example.test/api")

    def test_rejects_non_json_response(self):
        response = mock.Mock()
        response.json.side_effect = ValueError("no json")
        with mock.patch("rest_fetcher.client.requests.get", return_value=response):
            with self.assertRaises(APIError):
                fetch_json("https://example.test/api")


if __name__ == "__main__":
    unittest.main()
