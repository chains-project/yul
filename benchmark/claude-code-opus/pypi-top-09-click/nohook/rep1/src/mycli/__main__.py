"""Allow running as ``python -m mycli``."""

import sys

from mycli.cli import main

sys.exit(main())
