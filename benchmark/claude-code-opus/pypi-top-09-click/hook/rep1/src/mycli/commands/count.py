"""`count`: file/stdin input, boolean flags, and error handling."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from mycli.errors import CommandError

log = logging.getLogger(__name__)


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "count",
        help="count lines, words, and characters",
        description="Count lines, words, and characters in files (or stdin if none given).",
    )
    parser.add_argument("files", nargs="*", type=Path, metavar="FILE", help="files to read")
    parser.add_argument("-l", "--lines", action="store_true", help="only count lines")
    parser.add_argument("-w", "--words", action="store_true", help="only count words")
    parser.add_argument("-c", "--chars", action="store_true", help="only count characters")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.set_defaults(handler=run)


def count_text(text: str) -> dict[str, int]:
    return {"lines": text.count("\n"), "words": len(text.split()), "chars": len(text)}


def run(args: argparse.Namespace) -> int:
    selected = [k for k in ("lines", "words", "chars") if getattr(args, k)]
    fields = selected or ["lines", "words", "chars"]

    results: list[tuple[str, dict[str, int]]] = []
    if not args.files:
        results.append(("-", count_text(sys.stdin.read())))
    for path in args.files:
        log.info("reading %s", path)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise CommandError(f"{path}: no such file") from None
        except (OSError, UnicodeDecodeError) as exc:
            raise CommandError(f"{path}: {exc}") from None
        results.append((str(path), count_text(text)))

    if args.json:
        payload = [{"file": name, **{f: c[f] for f in fields}} for name, c in results]
        print(json.dumps(payload, indent=2))
    else:
        for name, counts in results:
            print(" ".join(f"{counts[f]:>8}" for f in fields), name)
    return 0
