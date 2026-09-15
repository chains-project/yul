import json
from pathlib import Path
from typing import Any

DEFAULT_STORE_PATH = Path.home() / ".taskcli" / "tasks.json"


def load_tasks(store_path: Path = DEFAULT_STORE_PATH) -> list[dict[str, Any]]:
    if not store_path.exists():
        return []
    with store_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: list[dict[str, Any]], store_path: Path = DEFAULT_STORE_PATH) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
