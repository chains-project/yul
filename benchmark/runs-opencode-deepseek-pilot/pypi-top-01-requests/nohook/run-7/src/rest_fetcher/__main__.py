"""Allow ``python -m rest_fetcher``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
