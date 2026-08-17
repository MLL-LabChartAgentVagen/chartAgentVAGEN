"""The fact table and its schema: what the data stage hands to view selection.

`TableSchema` is everything the single model call produced -- scenario prose,
column declarations, the dependency graph between numeric columns, and the
analysis intents. It holds no data values; those live in `FactTable`.

Keeping declarations and values apart is what lets chart feasibility be decided
before any row exists: cardinality, units, additivity and ordering are all
declared fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

ColumnKind = Literal["category", "time", "measure"]
Ordered = Literal["ordinal", "stage"]
Freq = Literal["daily", "weekly", "monthly"]

#: The six view classes, one per chart family. An analysis intent names one of
#: these; which chart type serves it is decided from the column declarations.
Family = Literal[
    "comparison",
    "trend",
    "composition",
    "relation",
    "distribution",
    "process",
]

#: Aggregates for the grouped-scalar projection shape, plus three placeholders
#: that stand for the other shapes: five-number summaries, bin counts, and no
#: aggregation at all.
Aggregate = Literal[
    "SUM", "AVG", "MAX", "MIN", "MEDIAN", "COUNT",
    "FIVE_NUM", "BIN_COUNT", "NONE",
]

#: Aggregates each kind of measure allows. Summing a non-additive measure -- a
#: ratio, a percentage, a score -- is never meaningful.
AGG_ADDITIVE: tuple[str, ...] = ("SUM", "AVG", "MAX", "MIN")
AGG_NON_ADDITIVE: tuple[str, ...] = ("AVG", "MEDIAN", "MAX", "MIN")


@dataclass(frozen=True)
class Column:
    """One declared column. Cardinality and the semantic fields are fixed at
    declaration time, and together they decide what can be drawn."""

    name: str
    kind: ColumnKind
    cardinality: int
    group: str | None = None          # which dimension group it belongs to
    parent: str | None = None         # the column above it in a hierarchy
    ordered: Ordered | None = None
    values: tuple[str, ...] = ()      # category columns
    unit: str | None = None           # numeric columns
    additive: bool | None = None      # numeric columns
    freq: Freq | None = None          # time columns
    start: str | None = None
    end: str | None = None
    derived_from: str | None = None   # a calendar field points at its time column


@dataclass(frozen=True)
class DimGroup:
    """A dimension group and its hierarchy chain, ordered root to leaf."""

    name: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class IntentBinding:
    """One analysis intent: a sentence, its target columns, an aggregate, a view class.

    Written in the same call as the columns, so the binding holds by construction
    rather than by inference. It is what a figure built to answer a question is
    constructed from, and the only source of caption text that cannot be read off
    the image itself.
    """

    index: int
    sentence: str
    columns: tuple[str, ...]
    aggregate: Aggregate
    family: Family


@dataclass(frozen=True)
class TableSchema:
    """The description of a generated table. Carries no values.

    `script` is the declaration text the table was generated from. It is kept
    because the table is reproducible from the declarations and a seed, which is
    only true if the declarations survive: without it a published table could
    never be rebuilt, only re-downloaded.
    """

    scenario_id: str
    scenario_title: str
    data_context: str
    columns: tuple[Column, ...]
    groups: tuple[DimGroup, ...] = ()
    dependencies: tuple[tuple[str, str], ...] = ()   # edges between numeric columns
    intents: tuple[IntentBinding, ...] = ()
    n_rows: int = 0
    script: str = ""

    def column(self, name: str) -> Column:
        for c in self.columns:
            if c.name == name:
                return c
        raise KeyError(f"undeclared column: {name}")

    def has(self, name: str) -> bool:
        return any(c.name == name for c in self.columns)

    def of_kind(self, kind: ColumnKind) -> tuple[Column, ...]:
        return tuple(c for c in self.columns if c.kind == kind)

    @property
    def categories(self) -> tuple[Column, ...]:
        return self.of_kind("category")

    @property
    def times(self) -> tuple[Column, ...]:
        return self.of_kind("time")

    @property
    def measures(self) -> tuple[Column, ...]:
        return self.of_kind("measure")

    def group_of(self, name: str) -> str | None:
        return self.column(name).group


@dataclass
class FactTable:
    """Row-level events. One row is one indivisible occurrence; aggregation happens
    only when a view is projected out of it."""

    scenario_id: str
    df: pd.DataFrame = field(repr=False)

    @property
    def n_rows(self) -> int:
        return len(self.df)
