"""Allow running as `python -m todo_cli`."""

import sys

from todo_cli.cli import main

sys.exit(main())
