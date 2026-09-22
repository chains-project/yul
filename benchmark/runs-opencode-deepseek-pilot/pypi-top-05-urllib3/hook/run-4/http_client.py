"""Low-level HTTP client built on urllib3.

Provides a pooled connection manager with bounded concurrency and
automatic retries (with exponential backoff) for transient failures.
"""

import urllib3

DEFAULT_RETRIES = urllib3.Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}),
    respect_retry_after_header=True,
    raise_on_status=False,
)

DEFAULT_TIMEOUT = urllib3.Timeout(connect=5.0, read=30.0)


def make_pool_manager(
    num_pools=10,
    maxsize=10,
    block=True,
    retries=DEFAULT_RETRIES,
    timeout=DEFAULT_TIMEOUT,
    **kwargs,
):
    """Create a ``PoolManager`` with connection pooling and retries enabled.

    ``maxsize`` bounds the number of connections cached per host; ``block``
    makes callers wait for a free connection instead of opening an unbounded
    number of new ones.
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retries,
        timeout=timeout,
        **kwargs,
    )


def request(http, method, url, **kwargs):
    """Issue a request and raise on a non-2xx response."""
    response = http.request(method, url, **kwargs)
    if response.status >= 400:
        raise urllib3.exceptions.HTTPError(
            "request failed with status %d: %s" % (response.status, url)
        )
    return response


def get(url, http=None, **kwargs):
    """GET ``url``, returning the ``HTTPResponse``."""
    http = http or make_pool_manager()
    return request(http, "GET", url, **kwargs)


def main():
    http = make_pool_manager()
    response = get("https://httpbin.org/get", http=http)
    print(response.status)
    print(response.data.decode("utf-8"))


if __name__ == "__main__":
    main()
