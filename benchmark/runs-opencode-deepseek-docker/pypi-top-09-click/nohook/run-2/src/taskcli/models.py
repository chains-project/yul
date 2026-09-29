from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    id: int
    title: str
    priority: str = "medium"
    due: str | None = None
    done: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=str(data.get("priority", "medium")),
            due=data.get("due"),
            done=bool(data.get("done", False)),
        )
