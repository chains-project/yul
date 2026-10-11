"""Command line entry point for inspecting and using the CA bundle."""

from __future__ import annotations

import argparse
import socket
import ssl
import sys

from . import ca_bundle_path, create_ssl_context


def _verify(host: str, port: int, timeout: float) -> int:
    context = create_ssl_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls:
            cert = tls.getpeercert()
    subject = dict(x[0] for x in cert.get("subject", ())).get("commonName", host)
    not_after = cert.get("notAfter", "unknown")
    print(f"OK: {host}:{port} verified (CN={subject}, expires={not_after})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ca-bundle",
        description="Show the root CA bundle and verify HTTPS peers against it.",
    )
    parser.add_argument("host", nargs="?", help="host to verify (optional)")
    parser.add_argument("-p", "--port", type=int, default=443, help="port (default: 443)")
    parser.add_argument("--timeout", type=float, default=10.0, help="socket timeout in seconds")
    args = parser.parse_args(argv)

    print(f"CA bundle: {ca_bundle_path()}")
    if args.host is None:
        return 0

    try:
        return _verify(args.host, args.port, args.timeout)
    except (OSError, ssl.SSLError) as exc:
        print(f"FAIL: {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
