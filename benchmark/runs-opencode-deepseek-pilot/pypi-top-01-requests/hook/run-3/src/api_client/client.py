"""HTTP helpers for talking to a JSON REST API."""

import requests

DEFAULT_TIMEOUT = 10.0


class ApiError(Exception):
    """Raised when an API request cannot be completed successfully."""


def _request(session, method, url, timeout, **kwargs):
    try:
        response = session.request(method, url, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        raise ApiError("request to {} failed: {}".format(url, exc)) from exc

    if not response.ok:
        raise ApiError(
            "request to {} returned HTTP {}: {}".format(
                url, response.status_code, response.text
            )
        )
    return response


def fetch_json(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT, session=None):
    """Fetch ``url`` and return the decoded JSON body."""
    session = session or requests.Session()
    response = _request(
        session, "GET", url, timeout, params=params, headers=headers
    )
    return response.json()


class ApiClient:
    """Thin wrapper around :class:`requests.Session` for a fixed base URL."""

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _url(self, path):
        return "{}/{}".format(self.base_url, path.lstrip("/"))

    def get(self, path, params=None, headers=None):
        """Perform a GET request and return the raw response."""
        return _request(
            self.session,
            "GET",
            self._url(path),
            self.timeout,
            params=params,
            headers=headers,
        )

    def get_json(self, path, params=None, headers=None):
        """Perform a GET request and return the decoded JSON body."""
        return self.get(path, params=params, headers=headers).json()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
