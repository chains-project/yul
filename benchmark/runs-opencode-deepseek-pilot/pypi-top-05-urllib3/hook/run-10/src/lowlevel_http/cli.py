import argparse
import sys

from .client import HttpClient


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch a URL with connection pooling and automatic retries."
    )
    parser.add_argument("url")
    parser.add_argument("-X", "--method", default="GET")
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--insecure", action="store_true")
    args = parser.parse_args(argv)

    from urllib3.util.retry import Retry

    retries = Retry(
        total=args.retries,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=None,
        raise_on_status=False,
    )

    client = HttpClient(
        retries=retries,
        timeout=args.timeout,
        cert_reqs="CERT_NONE" if args.insecure else "CERT_REQUIRED",
    )
    try:
        resp = client.request(args.method, args.url)
        sys.stdout.write(resp.data.decode("utf-8", "replace"))
        sys.stdout.write("\n")
        return 0 if resp.status < 400 else 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
