"""JSON-backed storage for tasks."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Task:
    id: int
    title: str
    priority: str
    done: bool = False


def load_tasks(path: Path) -> list[Task]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return [Task(**item) for item in data]


def save_tasks(path: Path, tasks: list[Task]) -> None:
    path.write_text(json.dumps([asdict(t) for t in tasks], indent=2))


def next_id(tasks: list[Task]) -> int:
    return max((t.id for t in tasks), default=0) + 1
