"""Mixing generated figures with real ones, and what each source may be asked.

The generated half is what carries position, provenance and paired styles; real
charts are what carry the distribution of how charts actually look. Training on
generated figures alone leaves the style gap between the two, which is the standing
objection to any purely synthetic work, so the mix is a hyper-parameter rather than
a choice made once.

What a source may be asked is decided by what its annotations support, not by how
much of it there is. A real chart-to-table dataset has a key and a value for every
point and no box for any of them: asking it for a region would be asking a model to
learn a box from a label that never had one.

    generated here      every target
    real charts         the key-and-value half of the grounded table, and the caption
    real page layouts   the page-element boxes

This module states that rule and applies it. Fetching and cleaning the real halves
is not done here -- they arrive as files, and what this decides is which targets each
of them is allowed to fill.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

Source = Literal["generated", "real_charts", "real_layouts"]

#: What each source's own annotations can answer. A target absent here is one that
#: source has no ground truth for.
SUPPORTED: dict[Source, frozenset[str]] = {
    "generated": frozenset({
        "grounded_table", "spot_check", "mark_locate", "mark_read", "drilldown",
        "page_elements", "legend_binding", "caption", "key_source"}),
    "real_charts": frozenset({"grounded_table", "caption"}),
    "real_layouts": frozenset({"page_elements"}),
}

#: Targets a source may fill only in part, and which part. A real chart's rows carry
#: a key and a value and no box, so its share of the grounded table is those columns.
PARTIAL: dict[tuple[Source, str], tuple[str, ...]] = {
    ("real_charts", "grounded_table"): ("key", "values"),
}


class MixError(ValueError):
    """A mix asks a source for something its annotations cannot answer."""


@dataclass(frozen=True)
class Portion:
    """One source's share of a training set, and where its samples come from."""

    source: Source
    weight: float
    path: str = ""

    def targets(self, wanted: Iterable[str]) -> dict[str, tuple[str, ...] | None]:
        """Which of the wanted targets this source fills, and which columns of each.

        `None` means the whole target; a tuple names the columns its annotations
        reach. Silently dropping the rest is what keeps a real chart from teaching a
        model that a box it never had is empty.
        """
        out: dict[str, tuple[str, ...] | None] = {}
        for name in wanted:
            if name in SUPPORTED[self.source]:
                out[name] = PARTIAL.get((self.source, name))
        return out


@dataclass(frozen=True)
class Mix:
    """The composition of a training set: which sources, in what proportion."""

    portions: tuple[Portion, ...] = ()

    def __post_init__(self) -> None:
        if not self.portions:
            raise MixError("a mix needs at least one source")
        if any(p.weight < 0 for p in self.portions):
            raise MixError("a share cannot be negative")
        if sum(p.weight for p in self.portions) <= 0:
            raise MixError("a mix whose shares are all zero has nothing in it")

    def share(self, source: Source) -> float:
        total = sum(p.weight for p in self.portions)
        return sum(p.weight for p in self.portions if p.source == source) / total

    def plan(self, wanted: Sequence[str]) -> dict[Source, dict[str, tuple[str, ...] | None]]:
        """Target by target, which sources fill it and with which columns."""
        return {p.source: p.targets(wanted) for p in self.portions}

    def check(self, wanted: Sequence[str]) -> None:
        """Every wanted target must have at least one source that can answer it."""
        covered = {name for p in self.portions for name in p.targets(wanted)}
        missing = sorted(set(wanted) - covered)
        if missing:
            raise MixError(
                f"no source in this mix can answer {missing}; "
                f"{sorted(SUPPORTED)} answer {sorted(set().union(*SUPPORTED.values()))}")


def from_config(config) -> Mix:
    """The mix a run was configured with.

    A configuration naming nothing is all generated, which is the mix a run of this
    repository alone produces.
    """
    raw = config.get("output.mix") or [{"source": "generated", "weight": 1.0}]
    return Mix(tuple(Portion(str(item["source"]), float(item.get("weight", 1.0)),
                             str(item.get("path", ""))) for item in raw))
