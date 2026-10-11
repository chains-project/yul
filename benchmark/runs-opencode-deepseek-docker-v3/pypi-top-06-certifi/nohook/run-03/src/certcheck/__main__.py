"""Command line entry point: verify one or more HTTPS URLs."""

from __future__ import annotations

import sys
import urllib.request

from .ssl_bundle import ssl_context


def fetch(url: str, timeout: float = 10.0) -> bytes:
    """Fetch ``url``, verifying the server certificate against the bundle."""
    with urllib.request.urlopen(url, context=ssl_context(), timeout=timeout) as response:
        return response.read()


def main(argv: list[str] | None = None) -> int:
    urls = list(sys.argv[1:] if argv is None else argv)
    if not urls:
        print("usage: certcheck URL [URL ...]", file=sys.stderr)
        return 2

    failed = False
    for url in urls:
        try:
            body = fetch(url)
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed = True
            print(f"{url}: FAILED ({exc})", file=sys.stderr)
        else:
            print(f"{url}: OK ({len(body)} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
