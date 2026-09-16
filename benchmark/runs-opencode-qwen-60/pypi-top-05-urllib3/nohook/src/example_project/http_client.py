import urllib3
from urllib3.util.retry import Retry
from urllib3.exceptions import RetryError, HTTPError


class HTTPClient:
    def __init__(
        self,
        pool_size=10,
        pool_block=False,
        max_retries=3,
        retry_statuses=(500, 502, 503, 504),
        backoff_factor=0.5,
        connect_timeout=10,
        read_timeout=30,
    ):
        self.retry = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=retry_statuses,
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"],
            raise_on_status=False,
        )

        self.http = urllib3.HTTPConnectionPool(
            host="localhost",
            port=80,
            maxsize=pool_size,
            block=pool_block,
            retries=self.retry,
        )

        self.https = urllib3.HTTPSConnectionPool(
            host="localhost",
            port=443,
            maxsize=pool_size,
            block=pool_block,
            retries=self.retry,
        )

        self._default_pool = self.https
        self._timeout = urllib3.Timeout(
            connect=connect_timeout,
            read=read_timeout,
        )

    def request(self, method, url, **kwargs):
        pool = self._get_pool(url)
        return pool.request(method, url, timeout=self._timeout, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("HEAD", url, **kwargs)

    def options(self, url, **kwargs):
        return self.request("OPTIONS", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def _get_pool(self, url):
        if url.startswith("https://"):
            return self.https
        return self.http

    def close(self):
        self.http.clear()
        self.https.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False