"""Connection pool and retry configuration."""

from __future__ import annotations

from dataclasses import dataclass, field

import urllib3
from urllib3.util import Retry, Timeout


@dataclass(frozen=True)
class ClientConfig:
    # Pooling
    num_pools: int = 10  # distinct hosts kept in the PoolManager
    maxsize: int = 10  # connections kept alive per host
    block: bool = False  # True: wait for a free connection instead of opening extras

    # Timeouts (seconds)
    connect_timeout: float = 5.0
    read_timeout: float = 30.0

    # Retries
    total_retries: int = 3
    backoff_factor: float = 0.5  # sleeps 0.5s, 1s, 2s, ... between attempts
    backoff_max: float = 30.0
    status_forcelist: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 500, 502, 503, 504})
    )
    allowed_methods: frozenset[str] = Retry.DEFAULT_ALLOWED_METHODS  # idempotent only
    respect_retry_after: bool = True

    def retry(self) -> Retry:
        return Retry(
            total=self.total_retries,
            backoff_factor=self.backoff_factor,
            backoff_max=self.backoff_max,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
            respect_retry_after_header=self.respect_retry_after,
            raise_on_status=False,  # return the final response instead of raising
        )

    def timeout(self) -> Timeout:
        return Timeout(connect=self.connect_timeout, read=self.read_timeout)


def build_pool_manager(config: ClientConfig | None = None, **pool_kwargs) -> urllib3.PoolManager:
    """Create a PoolManager with the given pooling, timeout, and retry policy.

    Extra keyword arguments (e.g. ``ca_certs``, ``cert_file``, ``headers``) are
    passed through to every underlying connection pool.
    """
    config = config or ClientConfig()
    return urllib3.PoolManager(
        num_pools=config.num_pools,
        maxsize=config.maxsize,
        block=config.block,
        retries=config.retry(),
        timeout=config.timeout(),
        **pool_kwargs,
    )
