"""Connection-pooled HTTP client with automatic retries, powered by urllib3."""

import json as _json

import urllib3
from urllib3.util.retry import Retry
from urllib3.util.timeout import Timeout


class HttpError(Exception):
    """Raised when a request fails after all retries have been exhausted."""

    def __init__(self, message, status=None, body=None):
        super(HttpError, self).__init__(message)
        self.status = status
        self.body = body


DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])


def build_retry(total=3, backoff_factor=0.5, status_forcelist=None, allowed_methods=None):
    """Construct a :class:`urllib3.util.Retry` policy.

    Retries are applied to connection errors and to the given HTTP statuses,
    with exponential backoff between attempts.
    """
    if status_forcelist is None:
        status_forcelist = DEFAULT_RETRY_STATUSES
    if allowed_methods is None:
        allowed_methods = DEFAULT_RETRY_METHODS

    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        raise_on_status=False,
        respect_retry_after_header=True,
    )


class HttpClient(object):
    """A small HTTP client wrapping :class:`urllib3.PoolManager`.

    Parameters
    ----------
    num_pools:
        Maximum number of distinct host pools to keep open.
    maxsize:
        Maximum number of connections to keep in each pool.
    block:
        If ``True``, block when the pool is exhausted instead of discarding
        connections.
    retries:
        Number of retry attempts per request, or a prebuilt ``Retry`` object.
    timeout:
        Per-request timeout in seconds, or a ``(connect, read)`` tuple.
    headers:
        Default headers applied to every request.
    """

    def __init__(
        self,
        num_pools=10,
        maxsize=10,
        block=False,
        retries=3,
        backoff_factor=0.5,
        timeout=10.0,
        headers=None,
        **pool_kwargs
    ):
        if isinstance(retries, Retry):
            retry_policy = retries
        else:
            retry_policy = build_retry(total=retries, backoff_factor=backoff_factor)

        self.headers = headers or {}
        self.timeout = self._make_timeout(timeout)
        self._pool = urllib3.PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=retry_policy,
            headers=self.headers,
            **pool_kwargs
        )

    @staticmethod
    def _make_timeout(timeout):
        if isinstance(timeout, Timeout):
            return timeout
        if isinstance(timeout, (tuple, list)):
            return Timeout(connect=timeout[0], read=timeout[1])
        return Timeout(connect=timeout, read=timeout)

    def request(self, method, url, body=None, headers=None, timeout=None, **kwargs):
        """Send a request, returning the raw :class:`urllib3.HTTPResponse`.

        Raises :class:`HttpError` on connection failures or non-2xx/3xx
        responses that survive the retry policy.
        """
        merged_headers = dict(self.headers)
        if headers:
            merged_headers.update(headers)

        try:
            response = self._pool.request(
                method,
                url,
                body=body,
                headers=merged_headers,
                timeout=timeout or self.timeout,
                **kwargs
            )
        except urllib3.exceptions.HTTPError as exc:
            raise HttpError("request to %s failed: %s" % (url, exc))

        if response.status >= 400:
            raise HttpError(
                "request to %s returned %d" % (url, response.status),
                status=response.status,
                body=response.data,
            )
        return response

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, body=None, **kwargs):
        return self.request("POST", url, body=body, **kwargs)

    def put(self, url, body=None, **kwargs):
        return self.request("PUT", url, body=body, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def get_json(self, url, **kwargs):
        response = self.get(url, **kwargs)
        return _json.loads(response.data.decode("utf-8"))

    def close(self):
        """Close all pooled connections."""
        self._pool.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
