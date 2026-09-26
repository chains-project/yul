import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_STORE = Path.home() / ".taskcli" / "tasks.json"


@dataclass
class Task:
    id: int
    title: str
    priority: str = "normal"
    done: bool = False


def load(store: Path = DEFAULT_STORE) -> list[Task]:
    if not store.exists():
        return []
    data = json.loads(store.read_text())
    return [Task(**item) for item in data]


def save(tasks: list[Task], store: Path = DEFAULT_STORE) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps([asdict(t) for t in tasks], indent=2))


def next_id(tasks: list[Task]) -> int:
    return max((t.id for t in tasks), default=0) + 1
