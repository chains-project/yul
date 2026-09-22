"""A small, dependency-light REST API client built on :mod:`requests`."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 10.0


class ApiError(Exception):
    """Raised when the API returns a non-successful response."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RestClient(object):
    """Thin wrapper around :class:`requests.Session` for JSON REST APIs.

    :param base_url: Root URL of the API, e.g. ``https://api.example.com``.
    :param timeout: Per-request timeout in seconds.
    :param retries: Number of retries for transient failures.
    :param headers: Default headers sent with every request.
    """

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT, retries=3, headers=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.session.headers.setdefault("Accept", "application/json")

        retry = Retry(
            total=retries,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"]),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _url(self, path):
        if path.startswith(("http://", "https://")):
            return path
        return "{0}/{1}".format(self.base_url, path.lstrip("/"))

    def request(self, method, path, params=None, json=None, **kwargs):
        """Perform a request and return the decoded JSON body.

        Raises :class:`ApiError` for 4xx/5xx responses.
        """
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(
            method, self._url(path), params=params, json=json, **kwargs
        )
        if not response.ok:
            raise ApiError(
                "HTTP {0} for {1} {2}".format(
                    response.status_code, method.upper(), response.url
                ),
                status_code=response.status_code,
                response=response,
            )
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def get(self, path, params=None, **kwargs):
        """Fetch a resource and return its decoded JSON body."""
        return self.request("GET", path, params=params, **kwargs)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
