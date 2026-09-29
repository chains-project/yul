"""Connection-pool and retry configuration backed by urllib3."""

from __future__ import annotations

from dataclasses import dataclass

import urllib3
from urllib3.util.retry import Retry

DEFAULT_RETRY_STATUSES: tuple[int, ...] = (429, 500, 502, 503, 504)

# Retry only idempotent methods; replaying a POST on a timeout risks duplicate writes.
DEFAULT_RETRY_METHODS: frozenset[str] = frozenset(
    {"GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"}
)


@dataclass(frozen=True)
class ClientConfig:
    """Tunable pooling and retry policy for a urllib3 :class:`PoolManager`."""

    total_retries: int = 3
    backoff_factor: float = 0.5
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    max_pool_size: int = 10
    pool_block: bool = False

    def build_retries(self) -> Retry:
        """Return a :class:`Retry` policy honoring ``Retry-After`` headers."""
        return Retry(
            total=self.total_retries,
            connect=self.total_retries,
            read=self.total_retries,
            status=self.total_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=DEFAULT_RETRY_STATUSES,
            allowed_methods=DEFAULT_RETRY_METHODS,
            respect_retry_after_header=True,
            raise_on_status=False,
        )

    def build_pool_manager(self) -> urllib3.PoolManager:
        """Return a pool manager with keep-alive pooling and the retry policy."""
        return urllib3.PoolManager(
            num_pools=8,
            maxsize=self.max_pool_size,
            block=self.pool_block,
            retries=self.build_retries(),
            timeout=urllib3.Timeout(connect=self.connect_timeout, read=self.read_timeout),
            headers={"User-Agent": f"httptool/{_version()}"},
        )


def _version() -> str:
    from . import __version__

    return __version__
