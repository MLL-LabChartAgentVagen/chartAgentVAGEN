"""Embedding 去重。

领域池的 topic / sub-topic 去重与场景去重是同一个判据，只是阈值不同，
所以只有这一个实现。`embed` 由调用方注入——换 embedding 服务不改这里。
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Sequence

Embed = Callable[[Sequence[str]], list[list[float]]]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class Deduper:
    """记住见过的文本，判断新来的一条与已有的是否过于接近。"""

    def __init__(self, embed: Embed, threshold: float = 0.85,
                 path: str | Path | None = None) -> None:
        self.embed = embed
        self.threshold = threshold
        self.path = Path(path) if path else None
        self.vectors: list[list[float]] = []
        self.texts: list[str] = []
        if self.path and self.path.exists():
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            self.texts, self.vectors = saved["texts"], saved["vectors"]

    def __len__(self) -> int:
        return len(self.texts)

    def similarity(self, text: str) -> float:
        if not self.vectors:
            return 0.0
        vector = self.embed([text])[0]
        return max(cosine(vector, other) for other in self.vectors)

    def is_duplicate(self, text: str) -> bool:
        return self.similarity(text) >= self.threshold

    def add(self, text: str) -> bool:
        """新的就收下并返回 True，撞了就返回 False。"""
        if self.is_duplicate(text):
            return False
        self.texts.append(text)
        self.vectors.append(self.embed([text])[0])
        self._save()
        return True

    def _save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"texts": self.texts, "vectors": self.vectors},
                                        ensure_ascii=False), encoding="utf-8")
