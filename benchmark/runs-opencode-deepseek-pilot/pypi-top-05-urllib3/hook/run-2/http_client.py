"""HTTP client with low-level connection control.

Uses urllib3 for connection pooling and automatic retries.
"""

import argparse
import json
import sys

import urllib3
from urllib3.util.retry import Retry


def build_pool(
    pool_connections=10,
    pool_maxsize=10,
    retries=3,
    backoff_factor=0.5,
    timeout=10.0,
):
    """Create a connection pool with automatic retries.

    pool_connections: number of distinct host pools to cache.
    pool_maxsize: max connections to keep per host pool.
    retries: total retry attempts across all retry categories.
    backoff_factor: sleep factor between retries (0.5, 1, 2, ...).
    timeout: per-request timeout in seconds.
    """
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"]),
        raise_on_status=False,
    )

    return urllib3.PoolManager(
        num_pools=pool_connections,
        maxsize=pool_maxsize,
        block=False,
        retries=retry,
        timeout=urllib3.Timeout(connect=timeout, read=timeout),
    )


def get(pool, url, headers=None):
    """Perform a GET request, returning status, headers, and body."""
    response = pool.request("GET", url, headers=headers or {})
    return response.status, dict(response.headers), response.data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--pool-maxsize", type=int, default=10)
    args = parser.parse_args(argv)

    pool = build_pool(
        pool_maxsize=args.pool_maxsize,
        retries=args.retries,
        timeout=args.timeout,
    )
    try:
        status, headers, body = get(pool, args.url)
    except urllib3.exceptions.HTTPError as exc:
        print("request failed: %s" % exc, file=sys.stderr)
        return 1

    print("status: %s" % status)
    print("headers: %s" % json.dumps(headers, indent=2))
    print("body bytes: %d" % len(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
