import requests

DEFAULT_TIMEOUT = 10.0


class APIError(Exception):
    pass


def fetch_json(url, *, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise APIError(f"request to {url} failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise APIError(f"response from {url} is not valid JSON") from exc
