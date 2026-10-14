"""Subcommand implementations.

Each module defines ``register(subparsers)``, which adds its parser and binds
a handler via ``set_defaults(func=...)``. Handlers take the parsed
``argparse.Namespace`` and return an exit code (``None`` means 0).
"""
