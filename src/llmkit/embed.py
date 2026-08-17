"""Deciding whether a piece of text is a near-duplicate of one already seen.

Two places need this and both need the same judgement with a different threshold:
building a pool of subject areas, where near-identical names make the pool smaller
than it looks, and generating scenarios, where the same subject area drawn twice
should not produce the same scenario twice.

The similarity function is injected, so the judgement can be as cheap or as
semantic as the caller wants. The default is `lexical`, which needs no service and
no model: it hashes character n-grams into a fixed-width vector.

What that default is good for, measured on short names: unrelated ones land around
0.1, rewordings of the same name around 0.65 to 0.87. So it separates them widely,
and a threshold near 0.65 is the right place to cut. On long prose the margin
collapses -- two unrelated paragraphs of English already score around 0.6, because
common word fragments dominate -- so compare short, specific text such as a name or
a title, not a paragraph.

What it cannot do is catch a paraphrase with no shared wording ("emergency
department" against "ED"). That needs a sentence embedding, which is one argument
away.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Callable, Sequence

Embed = Callable[[Sequence[str]], list[list[float]]]

#: Width of the vector `lexical` produces.
LEXICAL_DIM = 512

#: Character n-gram sizes hashed into that vector.
LEXICAL_NGRAMS = (3, 4, 5)

_SPACE = re.compile(r"\s+")


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def lexical(texts: Sequence[str], dim: int = LEXICAL_DIM) -> list[list[float]]:
    """Hash character n-grams into a normalised vector. No service, no model.

    Deterministic across processes: the hash is computed here rather than taken
    from the interpreter's salted `hash`.
    """
    out: list[list[float]] = []
    for text in texts:
        vector = [0.0] * dim
        clean = _SPACE.sub(" ", text.strip().lower())
        for n in LEXICAL_NGRAMS:
            for i in range(max(0, len(clean) - n + 1)):
                vector[_bucket(clean[i:i + n], dim)] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        out.append([v / norm for v in vector])
    return out


def _bucket(gram: str, dim: int) -> int:
    h = 2166136261
    for ch in gram.encode("utf-8"):
        h = ((h ^ ch) * 16777619) & 0xFFFFFFFF
    return h % dim


class Deduper:
    """Remembers what has been seen and answers whether something new is too close."""

    def __init__(self, embed: Embed | None = None, threshold: float = 0.85,
                 path: str | Path | None = None) -> None:
        self.embed = embed or lexical
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
        """Keep a new text and return True; reject a near-duplicate and return False."""
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
