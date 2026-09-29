from __future__ import annotations

import argparse
import sys

from http_client.client import build_pool, request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a URL with pooling and retries.")
    parser.add_argument("url", help="URL to request")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args(argv)

    pool = build_pool(total_retries=args.retries)
    resp = request(pool, args.method, args.url, preload_content=False)
    try:
        print(f"{resp.status} {resp.reason}")
        sys.stdout.buffer.write(resp.data)
    finally:
        resp.release_conn()
    return 0 if resp.status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
