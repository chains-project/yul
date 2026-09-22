# api-fetch

A small Python script for fetching data from a REST API over HTTP using
[`requests`](https://requests.readthedocs.io/).

## Install

```sh
uv venv
uv pip install -e ".[dev]"
```

## Usage

```sh
api-fetch /posts/1 --base-url https://jsonplaceholder.typicode.com
```

Or as a library:

```python
from api_fetch import ApiClient

with ApiClient("https://jsonplaceholder.typicode.com") as client:
    post = client.get("/posts/1")
    print(post["title"])
```

## Tests

```sh
pytest
```
