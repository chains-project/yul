"""Allow running the package with ``python -m clitool``."""

from __future__ import annotations

import sys

from clitool.cli import main

if __name__ == "__main__":
    sys.exit(main())
