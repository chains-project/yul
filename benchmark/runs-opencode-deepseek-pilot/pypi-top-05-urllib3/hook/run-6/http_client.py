from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, Optional

import urllib3
from urllib3.exceptions import HTTPError
from urllib3.util.retry import Retry

USER_AGENT = "http-pool-client/0.1.0"
RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_TIMEOUT = urllib3.Timeout(connect=5.0, read=30.0)


def build_pool_manager(
    num_pools: int = 10,
    maxsize: int = 10,
    retries: int = 3,
    backoff_factor: float = 0.5,
    block: bool = False,
) -> urllib3.PoolManager:
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        other=retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRY_STATUSES,
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    return urllib3.PoolManager(
        num_pools=num_pools,
        maxsize=maxsize,
        block=block,
        retries=retry,
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )


def fetch(pool: urllib3.PoolManager, url: str) -> dict:
    response = pool.request("GET", url, redirect=True)
    try:
        history = response.retries.history if response.retries else ()
        return {
            "url": url,
            "status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "retries": len(history),
            "length": len(response.data),
        }
    finally:
        response.release_conn()


def fetch_all(pool: urllib3.PoolManager, urls: Iterable[str]) -> list[dict]:
    return [fetch(pool, url) for url in urls]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch URLs over a pooled, retrying urllib3 client."
    )
    parser.add_argument("urls", nargs="+", help="one or more URLs to fetch")
    parser.add_argument("--num-pools", type=int, default=10, help="number of host pools")
    parser.add_argument("--maxsize", type=int, default=10, help="connections per host pool")
    parser.add_argument("--retries", type=int, default=3, help="retry attempts per request")
    parser.add_argument("--backoff-factor", type=float, default=0.5, help="retry backoff base")
    parser.add_argument("--json", action="store_true", help="emit results as JSON")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    pool = build_pool_manager(
        num_pools=args.num_pools,
        maxsize=args.maxsize,
        retries=args.retries,
        backoff_factor=args.backoff_factor,
    )

    try:
        results = fetch_all(pool, args.urls)
    except HTTPError as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        return 1
    finally:
        pool.clear()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(
                "{status} {url} ({length} bytes, {retries} retries)".format(**result)
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
