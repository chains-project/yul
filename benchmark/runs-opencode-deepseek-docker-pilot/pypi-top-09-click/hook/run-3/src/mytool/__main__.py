"""Allow running the tool as ``python -m mytool``."""

from mytool.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
