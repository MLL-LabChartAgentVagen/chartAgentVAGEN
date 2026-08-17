"""Content-addressed artifact storage.

Each stage stores its output under a hash of its input, so a hit is returned
without recomputing. Changing a later stage therefore does not re-run the earlier
ones, and an interrupted batch resumes where it stopped.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from hashlib import blake2b
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

from ..common import serde

T = TypeVar("T")

HASH_LEN = 16


def content_hash(obj: Any) -> str:
    """A stable hash of any interface object or plain value. Dictionaries are sorted,
    so key order does not change the result."""
    payload = serde.to_dict(obj) if is_dataclass(obj) and not isinstance(obj, type) else obj
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return blake2b(text.encode("utf-8"), digest_size=HASH_LEN // 2).hexdigest()


class Store:
    """Artifacts on disk, one directory per stage."""

    def __init__(self, root: str | Path, enabled: bool = True) -> None:
        self.root = Path(root)
        self.enabled = enabled

    def path(self, stage: str, key: Sequence[Any], suffix: str = ".json") -> Path:
        return self.root / stage / f"{content_hash(list(key))}{suffix}"

    def get_or_build(self, cls: type[T], stage: str, key: Sequence[Any],
                     build: Callable[[], T]) -> T:
        path = self.path(stage, key)
        if self.enabled and path.exists():
            return serde.load(cls, path)
        value = build()
        if self.enabled:
            serde.save(value, path)
        return value
