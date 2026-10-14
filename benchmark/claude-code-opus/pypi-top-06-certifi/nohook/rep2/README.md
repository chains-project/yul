# https-client

A small script that makes HTTPS requests verified against
[certifi](https://pypi.org/project/certifi/)'s curated Mozilla root CA bundle,
rather than relying on whatever (possibly stale or missing) CA store the host OS provides.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run https-client https://example.com
```

## Keeping certificates current

certifi publishes new releases whenever Mozilla's root store changes. Update with:

```sh
uv lock --upgrade-package certifi && uv sync
```
