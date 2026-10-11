from __future__ import annotations

import argparse


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("greet", help="Print a greeting")
    parser.add_argument(
        "name",
        nargs="?",
        default="world",
        help="who to greet (default: world)",
    )
    parser.add_argument(
        "-g",
        "--greeting",
        default="Hello",
        help="greeting word to use (default: Hello)",
    )
    parser.add_argument(
        "-u",
        "--uppercase",
        action="store_true",
        help="uppercase the greeting",
    )
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    message = f"{args.greeting}, {args.name}!"
    if args.uppercase:
        message = message.upper()
    if args.verbose:
        print(f"greet: name={args.name!r} greeting={args.greeting!r}")
    print(message)
    return 0
