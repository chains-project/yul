# rest-client

A small Python project with a script that fetches JSON data from a REST API
over HTTP. It is built on top of
[`requests`](https://requests.readthedocs.io/).

## Requirements

- Python 3.9+
- [`requests`](https://pypi.org/project/requests/) (installed automatically)

## Setup

Using a virtual environment is recommended:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv venv
uv pip install -e ".[dev]"
```

## Usage

Run the installed console script:

```bash
rest-client /users/1
```

or the module directly:

```bash
python -m rest_client /users/1
```

By default it talks to `https://jsonplaceholder.typicode.com`. Point it at any
REST API with `--base-url`, and pass query parameters or headers as needed:

```bash
rest-client /search \
  --base-url https://api.example.com \
  --param q=python \
  --header "Authorization=Bearer <token>" \
  --timeout 5
```

The decoded JSON response is printed to stdout, pretty-printed and sorted.

## Library use

```python
from rest_client import RestClient

with RestClient("https://jsonplaceholder.typicode.com") as client:
    user = client.get("/users/1")
    print(user["name"])
```

`RestClient.get` raises `rest_client.ApiError` on a non-2xx status or a
non-JSON body.

## Tests

```bash
pytest
```

## Project layout

```
.
├── pyproject.toml
├── README.md
├── src/
│   └── rest_client/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── client.py
└── tests/
    └── test_client.py
```
