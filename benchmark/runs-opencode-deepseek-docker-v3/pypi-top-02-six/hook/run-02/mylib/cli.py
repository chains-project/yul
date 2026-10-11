"""Command line entry point for :mod:`mylib`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse

from . import __version__
from .core import slugify


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mylib",
        description="Convert text into URL-friendly slugs.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument(
        "--unicode",
        dest="allow_unicode",
        action="store_true",
        help="keep non-ASCII word characters in the slug",
    )
    parser.add_argument("text", nargs="+", help="one or more strings to slugify")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    for value in args.text:
        print(slugify(value, allow_unicode=args.allow_unicode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
