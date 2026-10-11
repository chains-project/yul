from http_client_script.client import PooledClient, RetryPolicy


def main() -> None:
    with PooledClient(
        max_connections=50,
        max_keepalive_connections=10,
        transport_retries=3,
        retry_policy=RetryPolicy(max_attempts=5, base_delay=0.5),
    ) as client:
        response = client.get("https://example.com")
        print(response.status_code)
        print(response.text[:200])


if __name__ == "__main__":
    main()
