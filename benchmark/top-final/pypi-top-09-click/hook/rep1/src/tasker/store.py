from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Task:
    id: int
    text: str
    priority: str = "normal"
    done: bool = False


@dataclass
class TaskStore:
    path: Path
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "TaskStore":
        if not path.exists():
            return cls(path=path, tasks=[])
        data = json.loads(path.read_text())
        tasks = [Task(**item) for item in data]
        return cls(path=path, tasks=tasks)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(t) for t in self.tasks], indent=2))

    def next_id(self) -> int:
        return max((t.id for t in self.tasks), default=0) + 1

    def add(self, text: str, priority: str) -> Task:
        task = Task(id=self.next_id(), text=text, priority=priority)
        self.tasks.append(task)
        self.save()
        return task

    def find(self, task_id: int) -> Task | None:
        return next((t for t in self.tasks if t.id == task_id), None)

    def remove(self, task_id: int) -> bool:
        task = self.find(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        self.save()
        return True

    def mark_done(self, task_id: int) -> bool:
        task = self.find(task_id)
        if task is None:
            return False
        task.done = True
        self.save()
        return True
