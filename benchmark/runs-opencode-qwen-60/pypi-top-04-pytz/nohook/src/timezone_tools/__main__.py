"""Entry-point script for timezone-tools."""

import sys

from timezone_tools import world_clock_display


def main() -> None:
    """Run the world clock display."""
    print(world_clock_display())


if __name__ == "__main__":
    main()