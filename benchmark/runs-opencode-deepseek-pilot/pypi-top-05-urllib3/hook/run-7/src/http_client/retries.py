"""Retry configuration for the HTTP client."""

from urllib3.util.retry import Retry

DEFAULT_RETRIES = Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    redirect=5,
    backoff_factor=0.5,
    backoff_max=60.0,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE", "TRACE"}),
    respect_retry_after_header=True,
    raise_on_status=False,
)
