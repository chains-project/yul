#!/usr/bin/env python3
"""Example script using the pooled, retrying HTTP client."""

import sys

from http_client import HttpClient


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    url = argv[0] if argv else "https://httpbin.org/get"

    with HttpClient(pool_connections=20, pool_maxsize=20) as client:
        response = client.get(url)
        print("status: {}".format(response.status))
        print(response.data.decode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
