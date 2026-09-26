"""JSON-backed storage for tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_TASKS_FILE = Path.home() / ".taskcli" / "tasks.json"


def load_tasks(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def next_id(tasks: list[dict[str, Any]]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1
