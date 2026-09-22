"""HTTP client for talking to a REST API."""

import requests


class ApiError(Exception):
    """Raised when the API returns a non-success response."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ApiClient(object):
    """Thin wrapper around ``requests.Session`` for JSON REST APIs.

    Args:
        base_url: Root URL of the API, e.g. ``https://api.example.com/v1``.
        timeout: Default request timeout in seconds.
        headers: Extra headers sent with every request.
        session: Optional pre-configured ``requests.Session``.
    """

    def __init__(self, base_url, timeout=10.0, headers=None, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _url(self, path):
        return "{0}/{1}".format(self.base_url, path.lstrip("/"))

    def request(self, method, path, params=None, json=None, **kwargs):
        """Perform a request and return the decoded JSON body.

        Raises:
            ApiError: If the response status is not 2xx.
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
        if not response.content:
            return None
        return response.json()

    def get(self, path, params=None, **kwargs):
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path, json=None, **kwargs):
        return self.request("POST", path, json=json, **kwargs)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
