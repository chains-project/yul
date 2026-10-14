"""Allow running the tool with ``python -m mytool``."""

import sys

from mytool.cli import main

sys.exit(main())
