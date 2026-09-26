import urllib3

retries = urllib3.Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
)

http = urllib3.PoolManager(
    num_pools=10,
    maxsize=10,
    retries=retries,
)


def main() -> None:
    response = http.request("GET", "https://httpbin.org/get")
    print(response.status)
    print(response.data.decode("utf-8"))


if __name__ == "__main__":
    main()
