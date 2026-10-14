"""JSON-file persistence for todo items."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PRIORITIES = ("low", "normal", "high")


def default_path() -> Path:
    """Return the store path, honoring $TODO_FILE if set."""
    if env := os.environ.get("TODO_FILE"):
        return Path(env)
    return Path.home() / ".todo.json"


@dataclass
class Item:
    id: int
    text: str
    priority: str = "normal"
    tags: list[str] = field(default_factory=list)
    done: bool = False
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.items: list[Item] = []
        if path.exists():
            data = json.loads(path.read_text() or "[]")
            self.items = [Item(**raw) for raw in data]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps([asdict(i) for i in self.items], indent=2))
        tmp.replace(self.path)

    def add(self, text: str, priority: str = "normal", tags: list[str] | None = None) -> Item:
        next_id = max((i.id for i in self.items), default=0) + 1
        item = Item(id=next_id, text=text, priority=priority, tags=tags or [])
        self.items.append(item)
        return item

    def get(self, item_id: int) -> Item:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(item_id)

    def remove(self, item_id: int) -> Item:
        item = self.get(item_id)
        self.items.remove(item)
        return item
