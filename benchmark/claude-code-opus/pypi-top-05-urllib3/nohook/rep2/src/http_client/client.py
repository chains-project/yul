"""Thin wrapper around urllib3 exposing pooling, retry, and timeout knobs."""

from __future__ import annotations

from dataclasses import dataclass, field

import urllib3
from urllib3.util import Retry, Timeout


@dataclass
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
    backoff_factor: float = 0.5  # sleeps 0.5, 1, 2, ... between attempts
    backoff_max: float = 30.0
    status_forcelist: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 500, 502, 503, 504})
    )
    # Only retry idempotent methods by default; add POST at your own risk.
    allowed_methods: frozenset[str] = Retry.DEFAULT_ALLOWED_METHODS
    respect_retry_after: bool = True

    headers: dict[str, str] = field(
        default_factory=lambda: {"User-Agent": "http-client/0.1"}
    )


def build_retry(cfg: ClientConfig) -> Retry:
    return Retry(
        total=cfg.total_retries,
        backoff_factor=cfg.backoff_factor,
        backoff_max=cfg.backoff_max,
        status_forcelist=cfg.status_forcelist,
        allowed_methods=cfg.allowed_methods,
        respect_retry_after_header=cfg.respect_retry_after,
        raise_on_status=False,  # return the final response instead of raising
    )


def build_pool_manager(cfg: ClientConfig | None = None) -> urllib3.PoolManager:
    cfg = cfg or ClientConfig()
    return urllib3.PoolManager(
        num_pools=cfg.num_pools,
        maxsize=cfg.maxsize,
        block=cfg.block,
        retries=build_retry(cfg),
        timeout=Timeout(connect=cfg.connect_timeout, read=cfg.read_timeout),
        headers=cfg.headers,
    )
