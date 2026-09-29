"""Command line interface for :mod:`csvdata`."""

from __future__ import annotations

import argparse
import json
import sys

from .analysis import describe, summary, value_counts
from .cleaning import FILL_STRATEGIES, clean
from .errors import CsvDataError
from .loading import load_csv
from .render import format_record, format_table


def build_parser():
    parser = argparse.ArgumentParser(
        prog="csvdata",
        description="Load, clean and analyze tabular data from CSV files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(sub):
        sub.add_argument("path", help="path to the CSV file")
        sub.add_argument("--delimiter", default=",")
        sub.add_argument("--no-header", action="store_true")

    head = subparsers.add_parser("head", help="show the first rows")
    add_common(head)
    head.add_argument("-n", "--rows", type=int, default=10)

    show = subparsers.add_parser("describe", help="per-column summary statistics")
    add_common(show)

    stats = subparsers.add_parser("summary", help="dataset-level summary")
    add_common(stats)
    stats.add_argument("--json", action="store_true", help="emit JSON")

    counts = subparsers.add_parser("value-counts", help="count distinct values")
    add_common(counts)
    counts.add_argument("column")
    counts.add_argument("--normalize", action="store_true")

    cleaner = subparsers.add_parser("clean", help="clean a CSV and write it out")
    add_common(cleaner)
    cleaner.add_argument("-o", "--output", help="output path (default: stdout)")
    cleaner.add_argument("--keep-empty-rows", action="store_true")
    cleaner.add_argument("--drop-duplicates", action="store_true")
    cleaner.add_argument("--missing", choices=FILL_STRATEGIES)
    cleaner.add_argument("--fill-value")

    return parser


def _load(args):
    return load_csv(
        args.path,
        delimiter=args.delimiter,
        has_header=not args.no_header,
    )


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "summary" and args.json:
            print(json.dumps(summary(_load(args)), indent=2, default=str))
            return 0
        table = _load(args)
        if args.command == "head":
            output = format_table(table.head(args.rows))
        elif args.command == "describe":
            output = format_table(describe(table))
        elif args.command == "summary":
            output = format_record(summary(table))
        elif args.command == "value-counts":
            output = format_table(
                value_counts(table, args.column, normalize=args.normalize)
            )
        elif args.command == "clean":
            cleaned = clean(
                table,
                drop_empty=not args.keep_empty_rows,
                dedupe=args.drop_duplicates,
                missing=args.missing,
                value=args.fill_value,
            )
            if args.output:
                cleaned.to_csv(args.output, delimiter=args.delimiter)
                return 0
            output = format_table(cleaned)
        else:
            parser.error(f"unknown command: {args.command}")
            return 2
    except CsvDataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
