"""Command line entry point: fetch a URL with pooling and retries."""

from __future__ import annotations

import sys

from .client import build_default_client


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: httpclient URL [URL ...]", file=sys.stderr)
        return 2

    with build_default_client() as client:
        for url in args:
            resp = client.get(url)
            print(f"{resp.status} {url}")
            body = resp.data.decode("utf-8", errors="replace")
            print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
