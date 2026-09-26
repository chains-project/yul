# api-fetcher

Fetches data from a REST API over HTTP.

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```sh
python fetch_data.py [URL]
```

Defaults to `https://jsonplaceholder.typicode.com/posts/1` if no URL is given.
