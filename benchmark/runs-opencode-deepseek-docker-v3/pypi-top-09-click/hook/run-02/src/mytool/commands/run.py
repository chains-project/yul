from __future__ import annotations

import argparse
import sys


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("run", help="Run a named task")
    parser.add_argument(
        "task",
        choices=["build", "test", "deploy"],
        help="task to run",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="optional targets passed to the task",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="number of parallel jobs (default: 1)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="append",
        default=[],
        help="tag to apply (repeatable)",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress progress output",
    )
    output.add_argument(
        "--no-color",
        action="store_true",
        help="disable colored output",
    )
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    if args.jobs < 1:
        print("error: --jobs must be at least 1", file=sys.stderr)
        return 2
    summary = f"{args.task}: jobs={args.jobs} targets={args.targets} tags={args.tag}"
    if not args.quiet:
        flags = "no-color" if args.no_color else "color"
        print(f"[{flags}] {summary}")
    return 0
