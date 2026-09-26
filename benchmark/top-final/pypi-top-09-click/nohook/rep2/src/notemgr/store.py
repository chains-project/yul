import json
from pathlib import Path

DEFAULT_STORE = Path.home() / ".notemgr" / "notes.json"


def load_notes(store_path: Path) -> list[dict]:
    if not store_path.exists():
        return []
    return json.loads(store_path.read_text())


def save_notes(store_path: Path, notes: list[dict]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(notes, indent=2))


def next_id(notes: list[dict]) -> int:
    return max((note["id"] for note in notes), default=0) + 1
