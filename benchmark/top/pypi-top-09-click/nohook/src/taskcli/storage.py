import json
from pathlib import Path

DEFAULT_PATH = Path.home() / ".taskcli.json"


def load_tasks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(path: Path, tasks: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
