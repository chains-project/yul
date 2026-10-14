import argparse
import logging
import sys

from .client import ClientConfig, build_pool_manager

__all__ = ["ClientConfig", "build_pool_manager", "main"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch URLs over a pooled, retrying connection.")
    parser.add_argument("urls", nargs="+")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--pool-size", type=int, default=10)
    parser.add_argument("-v", "--verbose", action="store_true", help="log urllib3 connection/retry activity")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    http = build_pool_manager(ClientConfig(total_retries=args.retries, maxsize=args.pool_size))
    failed = False
    with http:
        for url in args.urls:
            try:
                resp = http.request(args.method, url)
            except Exception as exc:  # MaxRetryError, connection errors, etc.
                print(f"{url}: ERROR {exc}", file=sys.stderr)
                failed = True
                continue
            retries = resp.retries.history if resp.retries else ()
            print(f"{url}: {resp.status} ({len(resp.data)} bytes, {len(retries)} retries)")
            failed |= resp.status >= 400
    sys.exit(1 if failed else 0)
