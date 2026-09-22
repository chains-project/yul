"""Low-level HTTP client with connection pooling and automatic retries.

Uses urllib3 directly so the connection pool, retry policy, and timeouts are
all under our control rather than hidden behind a higher-level abstraction.
"""

import urllib3
from urllib3.util.retry import Retry

RETRY_STATUS_CODES = (429, 500, 502, 503, 504)

http = urllib3.PoolManager(
    num_pools=10,
    maxsize=10,
    block=False,
    timeout=urllib3.Timeout(connect=5.0, read=30.0),
    retries=Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        raise_on_status=False,
    ),
)


def fetch(url, method="GET", **kwargs):
    """Perform a request and return the response body as bytes."""
    response = http.request(method, url, **kwargs)
    if response.status >= 400:
        raise urllib3.exceptions.HTTPError(
            "request to %s failed with status %d" % (url, response.status)
        )
    return response.data


if __name__ == "__main__":
    print(fetch("https://httpbin.org/get").decode("utf-8"))
