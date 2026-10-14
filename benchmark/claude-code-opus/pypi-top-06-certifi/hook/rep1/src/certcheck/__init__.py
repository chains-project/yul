"""Verify HTTPS connections against the certifi root CA bundle."""

import argparse
import socket
import ssl
import sys

import certifi


def make_ssl_context() -> ssl.SSLContext:
    """Return a client SSL context that trusts only certifi's CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())


def check_host(host: str, port: int = 443, timeout: float = 10.0) -> dict:
    """Open a verified TLS connection to host:port and return the peer certificate."""
    ctx = make_ssl_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls:
            return tls.getpeercert()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", nargs="?", default="www.python.org")
    parser.add_argument("--port", type=int, default=443)
    args = parser.parse_args()

    print(f"CA bundle: {certifi.where()} (certifi {certifi.__version__})")
    try:
        cert = check_host(args.host, args.port)
    except ssl.SSLCertVerificationError as e:
        sys.exit(f"Verification FAILED for {args.host}: {e.verify_message}")
    except OSError as e:
        sys.exit(f"Connection error for {args.host}: {e}")

    subject = dict(x[0] for x in cert["subject"])
    issuer = dict(x[0] for x in cert["issuer"])
    print(f"Verified {args.host}:{args.port}")
    print(f"  subject: {subject.get('commonName')}")
    print(f"  issuer:  {issuer.get('organizationName')} / {issuer.get('commonName')}")
    print(f"  expires: {cert['notAfter']}")
