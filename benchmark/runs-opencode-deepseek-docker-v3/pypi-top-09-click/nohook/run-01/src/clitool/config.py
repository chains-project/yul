"""Read and write the tool's JSON configuration file."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from clitool.errors import CliError

log = logging.getLogger("clitool.config")

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "clitool" / "config.json"


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON object from *path*; return an empty dict if it is missing."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CliError(f"could not read config {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CliError(f"invalid JSON in config {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CliError(f"config {path} must contain a JSON object")
    return data


def save_config(path: Path, data: dict[str, Any]) -> None:
    """Write *data* to *path* as pretty-printed JSON."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise CliError(f"could not write config {path}: {exc}") from exc
    log.debug("wrote config to %s", path)
