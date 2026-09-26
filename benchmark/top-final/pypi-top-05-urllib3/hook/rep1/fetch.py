import urllib3

retries = urllib3.Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
http = urllib3.PoolManager(num_pools=10, maxsize=10, retries=retries)


def get(url: str) -> bytes:
    response = http.request("GET", url)
    return response.data


if __name__ == "__main__":
    print(get("https://httpbin.org/get"))
