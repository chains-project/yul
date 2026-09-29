import json
import os
from pathlib import Path

DEFAULT_STORE = Path.home() / ".taskbox" / "tasks.json"


class StoreError(Exception):
    """Raised when the task store cannot be read or written."""


def resolve_store(path=None):
    if path:
        return Path(path).expanduser()
    env = os.environ.get("TASKBOX_STORE")
    if env:
        return Path(env).expanduser()
    return DEFAULT_STORE


class Store:
    """JSON-backed task store."""

    def __init__(self, path=None):
        self.path = resolve_store(path)

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError) as exc:
            raise StoreError(f"could not read {self.path}: {exc}") from exc
        if not isinstance(data, list):
            raise StoreError(f"{self.path} does not contain a task list")
        return data

    def save(self, tasks):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + ".tmp")
            with tmp.open("w", encoding="utf-8") as handle:
                json.dump(tasks, handle, indent=2)
                handle.write("\n")
            tmp.replace(self.path)
        except OSError as exc:
            raise StoreError(f"could not write {self.path}: {exc}") from exc

    @staticmethod
    def next_id(tasks):
        return max((task.get("id", 0) for task in tasks), default=0) + 1
