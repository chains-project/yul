"""Allow running the tool with ``python -m mytool``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
