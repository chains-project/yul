from __future__ import annotations

import argparse
import sys
import urllib.request

from .ca import create_context


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch an HTTPS URL using certifi's CA bundle for verification."
    )
    parser.add_argument("url")
    args = parser.parse_args(argv)

    try:
        with urllib.request.urlopen(args.url, context=create_context()) as response:
            print(f"{response.status} {response.geturl()}")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
