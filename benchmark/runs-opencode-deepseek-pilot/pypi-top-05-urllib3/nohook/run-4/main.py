"""Example: pooled, retrying HTTP requests with urllib3."""

from httpclient import HttpClient, build_retry


def main():
    retry = build_retry(
        total=4,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
    )

    with HttpClient(num_pools=10, maxsize=10, block=True, retries=retry) as client:
        response = client.get("https://httpbin.org/get", timeout=10.0)
        print("status:", response.status)
        print("body:", response.data[:200])

        response.release_conn()


if __name__ == "__main__":
    main()
