"""JSON-backed persistence for tasks."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

PRIORITIES = ("low", "medium", "high")


def default_data_file() -> Path:
    override = os.environ.get("CLITOOL_DATA_FILE")
    if override:
        return Path(override)
    return Path.home() / ".clitool" / "tasks.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Task:
    id: int
    title: str
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    done: bool = False
    created: str = field(default_factory=_now)


class Store:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> List[Task]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Task(**item) for item in raw]

    def save(self, tasks: List[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(task) for task in tasks]
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def add(self, title: str, priority: str = "medium", tags: Optional[List[str]] = None) -> Task:
        if priority not in PRIORITIES:
            raise ValueError(f"unknown priority: {priority}")
        tasks = self.load()
        next_id = max((task.id for task in tasks), default=0) + 1
        task = Task(id=next_id, title=title, priority=priority, tags=list(tags or []))
        tasks.append(task)
        self.save(tasks)
        return task

    def get(self, task_id: int) -> Optional[Task]:
        for task in self.load():
            if task.id == task_id:
                return task
        return None

    def mark_done(self, task_id: int) -> Optional[Task]:
        tasks = self.load()
        for task in tasks:
            if task.id == task_id:
                task.done = True
                self.save(tasks)
                return task
        return None

    def remove(self, task_id: int) -> Optional[Task]:
        tasks = self.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                self.save(tasks[:index] + tasks[index + 1 :])
                return task
        return None
