import urllib3

# Reused across requests to the same host(s); handles connection pooling for us.
http = urllib3.PoolManager(
    retries=urllib3.Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
)


def fetch(url: str) -> bytes:
    response = http.request("GET", url)
    return response.data


if __name__ == "__main__":
    body = fetch("https://httpbin.org/get")
    print(body.decode())
