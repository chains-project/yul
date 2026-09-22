"""Low-level HTTP client with connection pooling and automatic retries.

Built on urllib3's PoolManager, which manages a pool of connections per host
so repeated requests reuse TCP/TLS sessions instead of reconnecting.
"""

import argparse
import logging
import sys

import urllib3
from urllib3.util.retry import Retry

LOGGER = logging.getLogger("http_client")

DEFAULT_TIMEOUT = urllib3.Timeout(connect=5.0, read=30.0)
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def build_retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=RETRY_STATUS_CODES,
):
    """Configure automatic retries for transient network and server errors."""
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "HEAD", "OPTIONS", "PUT", "DELETE"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )


def build_pool_manager(
    num_pools=10,
    maxsize=10,
    block=False,
    retries=None,
    timeout=DEFAULT_TIMEOUT,
    cert_reqs="CERT_REQUIRED",
):
    """Create a PoolManager with bounded connection pools.

    num_pools   number of distinct host pools to cache.
    maxsize     max connections kept per host pool.
    block       wait for a free connection instead of opening a new one.
    """
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retries if retries is not None else build_retry(),
        timeout=timeout,
        cert_reqs=cert_reqs,
        headers={"User-Agent": "http-client/0.1.0"},
    )


def request(http, method, url, body=None, headers=None, **kwargs):
    """Send a single request, reusing pooled connections and retry policy."""
    response = http.request(
        method,
        url,
        body=body,
        headers=headers,
        preload_content=False,
        **kwargs
    )
    try:
        payload = response.read()
    finally:
        response.release_conn()
    return response.status, payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("-d", "--data", default=None)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--num-pools", type=int, default=10)
    parser.add_argument("--maxsize", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    http = build_pool_manager(
        num_pools=args.num_pools,
        maxsize=args.maxsize,
        retries=build_retry(total=args.retries),
    )
    try:
        status, payload = request(
            http,
            args.method,
            args.url,
            body=args.data,
        )
    except urllib3.exceptions.MaxRetryError as exc:
        LOGGER.error("request failed after retries: %s", exc)
        return 1
    finally:
        http.clear()

    LOGGER.info("status=%s bytes=%d", status, len(payload))
    sys.stdout.write(payload.decode("utf-8", errors="replace"))
    if not payload.endswith(b"\n"):
        sys.stdout.write("\n")
    return 0 if status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
