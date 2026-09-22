import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


class ApiError(Exception):
    """Raised when a request to the API fails."""

    def __init__(self, message, status_code=None, response=None):
        # type: (str, Optional[int], Optional[requests.Response]) -> None
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RestClient:
    """Small wrapper around :class:`requests.Session` for JSON APIs."""

    def __init__(
        self,
        base_url="",
        timeout=DEFAULT_TIMEOUT,
        retries=DEFAULT_RETRIES,
        headers=None,
        session=None,
    ):
        # type: (str, float, int, Optional[Dict[str, str]], Optional[requests.Session]) -> None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()
        if headers:
            self.session.headers.update(headers)
        self._configure_retries(retries)

    def _configure_retries(self, retries):
        # type: (int) -> None
        retry = Retry(
            total=retries,
            backoff_factor=0.3,
            status_forcelist=RETRY_STATUS_CODES,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _build_url(self, path):
        # type: (str) -> str
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return "{}/{}".format(self.base_url, path.lstrip("/"))

    def request(self, method, path, **kwargs):
        # type: (str, str, Any) -> requests.Response
        url = self._build_url(path)
        kwargs.setdefault("timeout", self.timeout)
        logger.debug("%s %s", method, url)
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            raise ApiError("request to {} failed: {}".format(url, exc)) from exc
        if not response.ok:
            raise ApiError(
                "{} returned HTTP {}".format(url, response.status_code),
                status_code=response.status_code,
                response=response,
            )
        return response

    def get(self, path, params=None, headers=None):
        # type: (str, Optional[Dict[str, Any]], Optional[Dict[str, str]]) -> requests.Response
        return self.request("GET", path, params=params, headers=headers)

    def get_json(self, path, params=None, headers=None):
        # type: (str, Optional[Dict[str, Any]], Optional[Dict[str, str]]) -> Any
        return self.get(path, params=params, headers=headers).json()

    def close(self):
        # type: () -> None
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
