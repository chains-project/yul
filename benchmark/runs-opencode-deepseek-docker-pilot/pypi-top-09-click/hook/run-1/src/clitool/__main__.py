"""Allow running as ``python -m clitool``."""

import sys

from clitool.cli import main

if __name__ == "__main__":
    sys.exit(main())
