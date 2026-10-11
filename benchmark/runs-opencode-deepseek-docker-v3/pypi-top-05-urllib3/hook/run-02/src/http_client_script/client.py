"""Low-level HTTP client with connection pooling and automatic retries."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Self

import httpx

RETRYABLE_STATUS_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RetryPolicy:
    """Application-level retry policy with exponential backoff and jitter."""

    max_attempts: int = 5
    base_delay: float = 0.5
    max_delay: float = 30.0
    retryable_status_codes: frozenset[int] = field(
        default_factory=lambda: RETRYABLE_STATUS_CODES
    )

    def delay_for(self, attempt: int) -> float:
        """Full-jitter exponential backoff for a 1-based attempt number."""
        ceiling = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        return random.uniform(0, ceiling)


class PooledClient:
    """HTTP client with a fixed connection pool and layered retries.

    Two retry layers are available:
      * transport retries, which re-establish connections for connect
        errors/drops at the socket level; and
      * :class:`RetryPolicy`, which retries retryable status codes and
        transient errors with backoff.
    """

    def __init__(
        self,
        *,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        transport_retries: int = 3,
        timeout: float | httpx.Timeout = 10.0,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self.retry_policy = retry_policy or RetryPolicy()
        self._transport = httpx.HTTPTransport(limits=limits, retries=transport_retries)
        self._client = httpx.Client(transport=self._transport, timeout=timeout)

    def request(self, method: str, url: str, **kwargs: object) -> httpx.Response:
        """Send a request, retrying transient failures with backoff."""
        policy = self.retry_policy
        last_error: Exception | None = None

        for attempt in range(1, policy.max_attempts + 1):
            try:
                response = self._client.request(method, url, **kwargs)
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_error = exc
            else:
                if response.status_code not in policy.retryable_status_codes:
                    return response
                last_error = httpx.HTTPStatusError(
                    f"retryable status {response.status_code}",
                    request=response.request,
                    response=response,
                )

            if attempt == policy.max_attempts:
                break
            time.sleep(policy.delay_for(attempt))

        assert last_error is not None
        raise last_error

    def get(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
