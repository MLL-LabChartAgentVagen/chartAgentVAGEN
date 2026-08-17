"""Deriving a random stream for any part of the pipeline from one root seed.

Nothing reads global random state and nothing shares a generator: `derive` returns
a fresh stream every time, so the order in which parts of the pipeline run cannot
change what any of them produce.

Hashing uses blake2b rather than the built-in `hash`, which is salted per process
and therefore not reproducible across runs.
"""

from __future__ import annotations

from hashlib import blake2b

import numpy as np

_MASK = (1 << 63) - 1


def seed_of(root_seed: int, *parts: str | int) -> int:
    """A root seed and some identifiers to one stable 63-bit integer."""
    h = blake2b(digest_size=8)
    h.update(str(int(root_seed)).encode())
    for p in parts:
        h.update(b"\x1f")
        h.update(str(p).encode("utf-8"))
    return int.from_bytes(h.digest(), "big") & _MASK


def derive(root_seed: int, *parts: str | int) -> np.random.Generator:
    """The same seed and identifiers always give the same random stream."""
    return np.random.default_rng(seed_of(root_seed, *parts))
