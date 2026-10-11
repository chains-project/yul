"""Allow running the package with ``python -m clitool``."""

from __future__ import annotations

from clitool.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
