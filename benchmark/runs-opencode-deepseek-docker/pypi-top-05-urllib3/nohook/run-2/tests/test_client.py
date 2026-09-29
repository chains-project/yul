from __future__ import annotations

import urllib3
from urllib3.util.retry import Retry

from httptool import ClientConfig
from httptool.client import DEFAULT_RETRY_METHODS, DEFAULT_RETRY_STATUSES


def test_retries_reflect_config():
    retries = ClientConfig(total_retries=5, backoff_factor=1.5).build_retries()
    assert retries.total == 5
    assert retries.connect == 5
    assert retries.read == 5
    assert retries.status == 5
    assert retries.backoff_factor == 1.5
    assert retries.respect_retry_after_header is True


def test_retries_target_idempotent_methods_and_statuses():
    retries = ClientConfig().build_retries()
    assert set(retries.allowed_methods) == set(DEFAULT_RETRY_METHODS)
    assert set(retries.status_forcelist) == set(DEFAULT_RETRY_STATUSES)


def test_pool_manager_passes_pool_and_retry_config(monkeypatch):
    captured: dict = {}

    class FakePoolManager:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(urllib3, "PoolManager", FakePoolManager)
    ClientConfig(max_pool_size=7, pool_block=True).build_pool_manager()

    assert captured["maxsize"] == 7
    assert captured["block"] is True
    assert isinstance(captured["retries"], Retry)
    assert isinstance(captured["timeout"], urllib3.Timeout)
