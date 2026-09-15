# fetch-data

Fetches JSON data from a REST API over HTTP.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
python fetch_data.py [URL]
```

Defaults to `https://api.github.com` if no URL is given.
