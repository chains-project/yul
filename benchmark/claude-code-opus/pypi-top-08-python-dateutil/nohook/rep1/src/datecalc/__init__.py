"""Parse human-written date strings, including relative expressions like
'the first Monday of next month'."""

from datecalc.parse import DateParseError, resolve

__all__ = ["DateParseError", "resolve", "main"]


def main() -> None:
    from datecalc.cli import main as cli_main

    cli_main()
