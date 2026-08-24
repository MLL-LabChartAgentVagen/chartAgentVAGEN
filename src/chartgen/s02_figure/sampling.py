"""In what order the rotation tries chart families, and how that order can be changed.

The rotation used to walk the families in a fixed order, filling the ones the batch
did not have yet. That is one distribution among many, and which distribution a
batch was generated under belongs in the ablation table rather than in the code.

So the order comes from a named preset:

    uniform      the fixed walk, unchanged and bit-for-bit identical to it
    parsebench   the mix measured on a hundred published report pages
    a file       any other weights, by name

Three things this deliberately is not. It is not a quota: how many figures a
scenario yields is a result of sampling and admission, and a quota would also
strand the budget of a family this schema cannot draw at all. It is not keyed by
position, because adding a chart type would then silently shift every weight onto
the wrong family. And it does not reach back into the data stage's feasibility
check, because two presets have to run over the same fact table for their numbers
to be comparable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from ..interfaces.table import Family
from ..registry.charts import FAMILIES

#: The slot that stands for the types answering no view class.
FAMILYLESS: str = "familyless"

Slot = Family | None


@dataclass(frozen=True)
class Weights:
    """How often each family comes up. `by_name` of None is the fixed walk itself:
    with no weights there is no draw, so the order is exactly the declaration order."""

    name: str
    by_name: dict[str, float] | None = None

    def of(self, slot: Slot) -> float:
        key = FAMILYLESS if slot is None else slot
        return max(0.0, float((self.by_name or {}).get(key, 0.0)))

    def to_dict(self) -> dict:
        return {"preset": self.name, "weights": dict(self.by_name or {})}


#: Counts over the hundred-page sample, three models pooled, from
#: `parsebench/data/analysis/`: line 181, stacked_bar 128, bar 97, grouped_bar 90,
#: pie 21, area 5, scatter 5, and nothing at all in the distribution and process
#: families. Folded into families that is comparison 187, trend 186, composition
#: 154, relation 5.
#:
#: The two families the sample never showed keep a small floor rather than a zero.
#: A hundred pages is enough to say a family is rare and not enough to say it does
#: not exist, and a zero would take chart-type coverage away permanently in
#: exchange for a proportion the report itself calls weakly evidenced.
PARSEBENCH_WEIGHTS: dict[str, float] = {
    "comparison": 0.34,
    "trend": 0.34,
    "composition": 0.28,
    "relation": 0.02,
    "distribution": 0.02,
    "process": 0.02,
    FAMILYLESS: 0.05,
}

PRESETS: dict[str, Weights] = {
    "uniform": Weights("uniform", None),
    "parsebench": Weights("parsebench", PARSEBENCH_WEIGHTS),
}


def load(preset: str | None) -> Weights:
    """A preset by name, or a JSON file of weights keyed by family name."""
    if not preset or preset in PRESETS:
        return PRESETS[preset or "uniform"]
    path = Path(preset)
    if not path.exists():
        raise FileNotFoundError(
            f"no such family-weight preset: {preset}. Known presets are "
            f"{sorted(PRESETS)}, or give a path to a JSON file of weights by family name.")
    raw = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(raw) - set(FAMILIES) - {FAMILYLESS}
    if unknown:
        raise ValueError(f"weights name families that do not exist: {sorted(unknown)}")
    return Weights(path.stem, {str(k): float(v) for k, v in raw.items()})


def slots(max_tier: int = 3) -> tuple[Slot, ...]:
    """Every slot the rotation may draw from: the six view classes, then the types
    that answer none of them."""
    from ..registry.charts import familyless

    reachable = any(c.tier <= max_tier for c in familyless())
    return (*FAMILIES, *((None,) if reachable else ()))


def rotation_order(candidates: Sequence[Slot], seen: Iterable[Slot],
                   rng: np.random.Generator, weights: Weights) -> list[Slot]:
    """The order to try slots in: the ones the batch does not have yet, then the rest.

    Filling the gaps first is what makes coverage the point of this path. The
    weights only decide the order inside each of those two halves, so a preset
    shifts the mix without ever locking a family out.
    """
    already = set(seen)
    gaps = [s for s in candidates if s not in already]
    rest = [s for s in candidates if s in already]
    if weights.by_name is None:
        return gaps + rest
    return _weighted_shuffle(gaps, rng, weights) + _weighted_shuffle(rest, rng, weights)


def _weighted_shuffle(items: Sequence[Slot], rng: np.random.Generator,
                      weights: Weights) -> list[Slot]:
    """Draw without replacement, each item's chance proportional to its weight.

    A zero-weight item still comes out, just last: the weights order the rotation,
    they do not veto a family.
    """
    pool = list(items)
    out: list[Slot] = []
    while pool:
        w = np.array([weights.of(s) for s in pool], dtype=float)
        if w.sum() <= 0:
            out += pool
            break
        pick = int(rng.choice(len(pool), p=w / w.sum()))
        out.append(pool.pop(pick))
    return out
