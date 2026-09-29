from __future__ import annotations

import sys
from dataclasses import dataclass

from .storage import Storage


@dataclass
class Context:
    storage: Storage
    verbose: bool = False

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"task: {message}", file=sys.stderr)
