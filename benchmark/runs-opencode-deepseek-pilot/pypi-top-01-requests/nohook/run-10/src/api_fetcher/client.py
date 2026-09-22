"""HTTP client helpers for fetching JSON data from a REST API."""

import requests

DEFAULT_TIMEOUT = 10.0
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "api-fetcher/0.1.0",
}


class ApiError(Exception):
    """Raised when a request to the API fails."""

    def __init__(self, message, status_code=None, url=None):
        super(ApiError, self).__init__(message)
        self.status_code = status_code
        self.url = url


def fetch_json(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT, session=None):
    """Fetch ``url`` and return the decoded JSON body.

    Args:
        url: Absolute URL of the REST endpoint.
        params: Optional mapping of query string parameters.
        headers: Optional mapping of extra request headers.
        timeout: Request timeout in seconds.
        session: Optional pre-configured :class:`requests.Session`.

    Returns:
        The parsed JSON payload (usually a ``dict`` or ``list``).

    Raises:
        ApiError: If the request fails, times out, or returns a non-2xx status.
    """
    request_headers = dict(DEFAULT_HEADERS)
    if headers:
        request_headers.update(headers)

    http = session or requests

    try:
        response = http.get(
            url,
            params=params,
            headers=request_headers,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ApiError("Request to %s failed: %s" % (url, exc), url=url)

    if not response.ok:
        raise ApiError(
            "Request to %s returned status %s" % (url, response.status_code),
            status_code=response.status_code,
            url=url,
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(
            "Response from %s was not valid JSON: %s" % (url, exc),
            status_code=response.status_code,
            url=url,
        )
