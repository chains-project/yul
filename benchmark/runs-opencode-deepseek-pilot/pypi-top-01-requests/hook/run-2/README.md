# rest-fetcher

A small Python project that fetches data from a REST API over HTTP using
[`requests`](https://requests.readthedocs.io/).

## Setup

```bash
uv venv
uv pip install -e ".[dev]"
```

Or with plain pip:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Command line:

```bash
rest-fetcher https://api.github.com/repos/psf/requests \
  -H "Accept=application/vnd.github+json" \
  -p per_page=5
```

As a library:

```python
from rest_fetcher import fetch_json

data = fetch_json("https://api.github.com/repos/psf/requests")
print(data["full_name"])
```

## Tests

```bash
pytest
```
