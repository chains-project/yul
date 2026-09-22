# rest-fetch

A small Python project that fetches data from a REST API over HTTP using
[`requests`](https://requests.readthedocs.io/).

## Layout

```
src/rest_fetch/client.py   RestClient wrapper around requests.Session
src/rest_fetch/cli.py      `rest-fetch` command line entry point
tests/test_client.py       unit tests (no network access required)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Usage

As a library:

```python
from rest_fetch import RestClient

with RestClient("https://api.example.com") as client:
    users = client.get("/users", params={"limit": 10})
```

From the command line:

```bash
python -m rest_fetch.cli https://api.github.com/repos/psf/requests -p foo=bar
```

## Tests

```bash
pytest
```
