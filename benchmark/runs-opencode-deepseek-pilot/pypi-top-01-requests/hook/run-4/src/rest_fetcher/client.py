"""HTTP client for fetching JSON data from a REST API."""

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, RequestException
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3


class FetchError(Exception):
    """Raised when a request to the API cannot be completed."""


class ApiClient(object):
    """Thin wrapper around :mod:`requests` for talking to a JSON REST API.

    Parameters
    ----------
    base_url:
        Root URL of the API, e.g. ``"https://api.example.com/v1"``.
    timeout:
        Per-request timeout in seconds.
    retries:
        Number of times to retry transient failures (connection errors and
        responses with status 429, 500, 502, 503 or 504).
    headers:
        Extra headers merged into every request, e.g. an API key.
    """

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES,
                 headers=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if headers:
            self.session.headers.update(headers)

        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _url(self, path):
        if path.startswith(("http://", "https://")):
            return path
        return "{}/{}".format(self.base_url, path.lstrip("/"))

    def get(self, path, params=None):
        """Fetch ``path`` and return the decoded JSON body.

        Raises :class:`FetchError` on any network or HTTP error.
        """
        url = self._url(path)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except HTTPError as exc:
            raise FetchError(
                "HTTP {} for {}: {}".format(
                    exc.response.status_code, url, exc.response.reason
                )
            )
        except RequestException as exc:
            raise FetchError("Request to {} failed: {}".format(url, exc))

        try:
            return response.json()
        except ValueError as exc:
            raise FetchError("Response from {} was not valid JSON: {}".format(url, exc))

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
