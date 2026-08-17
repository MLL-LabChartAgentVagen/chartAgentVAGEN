"""内容哈希与产物落盘。

每个阶段的产物按输入的内容哈希落盘，命中直接返回。改 03 不会触发 01–02 重跑，
这同时就是断点续跑。
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass
from hashlib import blake2b
from pathlib import Path
from typing import Any, Callable, Sequence, TypeVar

from ..interfaces import io

T = TypeVar("T")

HASH_LEN = 16


def content_hash(obj: Any) -> str:
    """任何接口对象或普通值的稳定哈希。字典按键排序，与书写顺序无关。"""
    payload = io.to_dict(obj) if is_dataclass(obj) and not isinstance(obj, type) else obj
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return blake2b(text.encode("utf-8"), digest_size=HASH_LEN // 2).hexdigest()


class Store:
    """`out/<run_id>/` 下按阶段分目录的产物缓存。"""

    def __init__(self, root: str | Path, enabled: bool = True) -> None:
        self.root = Path(root)
        self.enabled = enabled

    def path(self, stage: str, key: Sequence[Any], suffix: str = ".json") -> Path:
        return self.root / stage / f"{content_hash(list(key))}{suffix}"

    def get_or_build(self, cls: type[T], stage: str, key: Sequence[Any],
                     build: Callable[[], T]) -> T:
        path = self.path(stage, key)
        if self.enabled and path.exists():
            return io.load(cls, path)
        value = build()
        if self.enabled:
            io.save(value, path)
        return value
