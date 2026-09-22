# api-fetch

Fetch data from a REST API over HTTP.

## Setup

```sh
uv sync --extra dev
```

## Usage

```sh
# print the JSON body of an endpoint
uv run api-fetch https://api.github.com/repos/python/cpython

# with query parameters and headers
uv run api-fetch https://httpbin.org/get \
  --param q=python \
  --header X-Token=secret
```

Or use it as a library:

```python
from api_fetch import fetch_json

data = fetch_json("https://api.github.com/repos/python/cpython")
print(data["stargazers_count"])
```

`fetch_json` raises `api_fetch.ApiError` on a non-2xx response, a network
failure, or an invalid JSON body.

## Tests

```sh
uv run pytest
```
