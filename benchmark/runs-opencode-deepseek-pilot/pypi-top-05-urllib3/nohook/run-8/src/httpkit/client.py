import urllib3
from urllib3.util.retry import Retry

DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
DEFAULT_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


def default_retries(total=3, backoff_factor=0.5):
    return Retry(
        total=total,
        connect=total,
        read=total,
        status=total,
        backoff_factor=backoff_factor,
        status_forcelist=DEFAULT_RETRY_STATUSES,
        allowed_methods=DEFAULT_RETRY_METHODS,
        raise_on_status=False,
        respect_retry_after_header=True,
    )


class HttpClient:
    def __init__(
        self,
        retries=None,
        timeout=None,
        num_pools=10,
        maxsize=10,
        block=False,
        headers=None,
        **pool_kwargs
    ):
        if retries is None:
            retries = default_retries()
        if timeout is None:
            timeout = urllib3.Timeout(connect=5.0, read=30.0)
        elif isinstance(timeout, (int, float)):
            timeout = urllib3.Timeout(connect=timeout, read=timeout)

        self.retries = retries
        self.timeout = timeout
        self.pool = urllib3.PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            headers=headers,
            retries=retries,
            timeout=timeout,
            **pool_kwargs
        )

    def request(self, method, url, **kwargs):
        kwargs.setdefault("retries", self.retries)
        kwargs.setdefault("timeout", self.timeout)
        return self.pool.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def close(self):
        self.pool.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
