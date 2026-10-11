"""Allow running the package with ``python -m mytool``."""

from __future__ import annotations

import sys

from mytool.cli import main

if __name__ == "__main__":
    sys.exit(main())
