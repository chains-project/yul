"""Command line interface: ``python -m datalib``."""

from __future__ import annotations

import argparse
import csv
import json
import sys

from . import __version__
from .analysis import describe
from .cleaning import clean
from .exceptions import DataLibError
from .loader import load_csv
from .table import Table


def _write_csv(table: Table, stream) -> None:
    writer = csv.writer(stream)
    writer.writerow(table.columns)
    for row in table.rows:
        writer.writerow(["" if row[c] is None else row[c] for c in table.columns])


def _add_load_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", help="path to the CSV file")
    parser.add_argument("--delimiter", default=",", help="field delimiter")
    parser.add_argument(
        "--infer", action="store_true", help="infer column types while loading"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datalib", description="Load, clean and analyze CSV data."
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    describe_cmd = sub.add_parser("describe", help="print summary statistics as JSON")
    _add_load_options(describe_cmd)

    head_cmd = sub.add_parser("head", help="print the first rows as CSV")
    _add_load_options(head_cmd)
    head_cmd.add_argument("-n", type=int, default=5, help="number of rows")

    clean_cmd = sub.add_parser("clean", help="clean a CSV and write it to stdout")
    _add_load_options(clean_cmd)
    clean_cmd.add_argument("--drop-dupes", action="store_true")
    clean_cmd.add_argument(
        "--fill-strategy",
        choices=["mean", "median", "mode", "ffill", "bfill"],
        default=None,
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        table = load_csv(
            args.path,
            delimiter=args.delimiter,
            infer_types=args.infer,
        )
        if args.command == "describe":
            print(json.dumps(describe(table), indent=2, default=str))
        elif args.command == "head":
            _write_csv(table.head(args.n), sys.stdout)
        elif args.command == "clean":
            cleaned = clean(
                table,
                drop_dupes=args.drop_dupes,
                fill_strategy=args.fill_strategy,
            )
            _write_csv(cleaned, sys.stdout)
    except (DataLibError, FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
