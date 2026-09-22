"""Low-level HTTP client built on urllib3.

Provides explicit control over connection pooling, timeouts and automatic
retries while keeping a single reusable :class:`urllib3.PoolManager`.
"""

import urllib3
from urllib3.util.retry import Retry


class HttpConfig(object):
    """Configuration for :class:`HttpClient`.

    :param num_pools: Number of distinct host pools the manager keeps open.
    :param maxsize: Maximum connections retained per host pool.
    :param block: Whether to block when the pool is exhausted instead of
        creating a new connection.
    :param retries: Total number of retry attempts per request.
    :param backoff_factor: Base factor for exponential backoff between retries.
    :param status_forcelist: HTTP status codes that should trigger a retry.
    :param allowed_methods: Methods that are safe to retry.
    :param connect_timeout: Seconds allowed for establishing a connection.
    :param read_timeout: Seconds allowed for reading a response.
    """

    def __init__(
        self,
        num_pools=10,
        maxsize=10,
        block=False,
        retries=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"),
        connect_timeout=5.0,
        read_timeout=30.0,
    ):
        self.num_pools = num_pools
        self.maxsize = maxsize
        self.block = block
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = tuple(status_forcelist)
        self.allowed_methods = tuple(allowed_methods)
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout


class HttpClient(object):
    """Reusable HTTP client with pooling and retries.

    Use as a context manager so the underlying connection pools are released::

        with HttpClient() as client:
            response = client.get("https://example.com")
    """

    def __init__(self, config=None):
        self.config = config or HttpConfig()

        retry = Retry(
            total=self.config.retries,
            connect=self.config.retries,
            read=self.config.retries,
            redirect=self.config.retries,
            status=self.config.retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.status_forcelist,
            allowed_methods=self.config.allowed_methods,
            raise_on_status=False,
        )

        self._timeout = urllib3.Timeout(
            connect=self.config.connect_timeout,
            read=self.config.read_timeout,
        )

        self._manager = urllib3.PoolManager(
            num_pools=self.config.num_pools,
            maxsize=self.config.maxsize,
            block=self.config.block,
            retries=retry,
            timeout=self._timeout,
        )

    def request(self, method, url, **kwargs):
        """Perform a request with the shared pool and retry policy."""
        return self._manager.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def close(self):
        """Release all pooled connections."""
        self._manager.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
