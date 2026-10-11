"""The ``info`` subcommand: print environment details, optionally as JSON."""

from __future__ import annotations

import argparse
import json
import platform
import sys

from clitool import __version__


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        "info",
        help="Show version and environment information.",
        description="Show version and environment information.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit the information as JSON.",
    )
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> int:
    info = {
        "clitool": __version__,
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    if args.as_json:
        print(json.dumps(info, indent=2))
    else:
        for key, value in info.items():
            print(f"{key:>14}: {value}")
    return 0
