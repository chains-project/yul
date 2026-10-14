"""Allow running as `python -m mycli`."""

from mycli.cli import main

raise SystemExit(main())
