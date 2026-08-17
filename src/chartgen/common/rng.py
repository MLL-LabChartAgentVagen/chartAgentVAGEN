"""由根种子派生各阶段子种子。

一个根种子，按 `(scenario_id, 阶段名, 序号)` 派生。任何阶段不读全局随机状态，
也不共享一个 Generator——`derive` 每次返回一个全新的流，调用顺序因此不影响结果。

用 blake2b 而不是 `hash()`：后者每个进程加盐，跨进程不可复现。
"""

from __future__ import annotations

from hashlib import blake2b

import numpy as np

_MASK = (1 << 63) - 1


def seed_of(root_seed: int, *parts: str | int) -> int:
    """`(根种子, 若干标识) -> 一个稳定的 63 位整数`。"""
    h = blake2b(digest_size=8)
    h.update(str(int(root_seed)).encode())
    for p in parts:
        h.update(b"\x1f")
        h.update(str(p).encode("utf-8"))
    return int.from_bytes(h.digest(), "big") & _MASK


def derive(root_seed: int, *parts: str | int) -> np.random.Generator:
    """同样的 `(root_seed, parts)` 必得同样的随机流。"""
    return np.random.default_rng(seed_of(root_seed, *parts))
