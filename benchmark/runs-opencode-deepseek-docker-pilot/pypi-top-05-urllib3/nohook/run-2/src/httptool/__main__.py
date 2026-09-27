"""Command-line entry point: fetch one or more URLs through a pooled client."""

from __future__ import annotations

import sys

from .client import ClientConfig


def fetch(url: str, *, config: ClientConfig | None = None) -> int:
    """GET ``url`` and print a one-line summary. Returns 0 on 2xx/3xx, else 1."""
    config = config or ClientConfig()
    http = config.build_pool_manager()
    try:
        response = http.request("GET", url)
        print(f"{response.status} {url} ({len(response.data)} bytes)")
        return 0 if response.status < 400 else 1
    finally:
        http.clear()


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: httptool URL [URL ...]", file=sys.stderr)
        return 2
    status = 0
    for url in argv:
        status |= fetch(url)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
