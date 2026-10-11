"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3


@dataclass(frozen=True)
class Settings:
    """Runtime settings for :class:`~api_client.client.APIClient`."""

    base_url: str
    token: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES

    @classmethod
    def load(
        cls,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> Settings:
        """Build settings from ``API_*`` environment variables.

        Explicit ``base_url`` / ``timeout`` arguments take precedence over the
        ``API_BASE_URL`` / ``API_TIMEOUT`` environment variables.
        """
        resolved_url = base_url or os.environ.get("API_BASE_URL")
        if not resolved_url:
            raise ValueError("API_BASE_URL environment variable or --base-url is required")

        env_timeout = float(os.environ.get("API_TIMEOUT", DEFAULT_TIMEOUT))
        return cls(
            base_url=resolved_url,
            token=os.environ.get("API_TOKEN"),
            timeout=timeout if timeout is not None else env_timeout,
            retries=int(os.environ.get("API_RETRIES", DEFAULT_RETRIES)),
        )

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings purely from ``API_*`` environment variables."""
        return cls.load()
