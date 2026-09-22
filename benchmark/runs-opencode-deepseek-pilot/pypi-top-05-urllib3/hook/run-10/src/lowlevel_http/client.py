import urllib3
from urllib3.util.retry import Retry

DEFAULT_RETRY = Retry(
    total=3,
    connect=3,
    read=3,
    redirect=3,
    status=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(
        ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    ),
    raise_on_status=False,
)


class HttpClient:
    """Thin wrapper around urllib3.PoolManager.

    Gives low-level control over connections: pool sizing, timeouts,
    TLS verification and automatic retries with exponential backoff.
    """

    def __init__(
        self,
        num_pools=10,
        maxsize=10,
        block=False,
        retries=None,
        timeout=None,
        cert_reqs="CERT_REQUIRED",
        ca_certs=None,
        headers=None,
    ):
        self.retries = retries if retries is not None else DEFAULT_RETRY
        self.timeout = timeout
        self.pool = urllib3.PoolManager(
            num_pools=num_pools,
            maxsize=maxsize,
            block=block,
            retries=self.retries,
            timeout=self.timeout,
            cert_reqs=cert_reqs,
            ca_certs=ca_certs,
            headers=headers,
        )

    def request(self, method, url, **kwargs):
        kwargs.setdefault("retries", self.retries)
        return self.pool.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def close(self):
        self.pool.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
