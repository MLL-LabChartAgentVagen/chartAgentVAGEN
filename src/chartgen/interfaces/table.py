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
Freq = Literal["daily", "weekly", "monthly", "quarterly", "yearly"]

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

#: How each aggregate reads in a sentence, on an axis title, and in a caption. One
#: table, because those are three renderings of the same fact and they have to agree:
#: an axis reading "Five_Num wait minutes" is not describing anything a reader knows.
#: The last two name a shape of projection rather than one number, so they read as a
#: phrase about the column instead of a word in front of it.
AGGREGATE_PHRASE: dict[str, str] = {
    "SUM": "total", "AVG": "average", "MAX": "highest", "MIN": "lowest",
    "MEDIAN": "median", "COUNT": "the number of records",
    "FIVE_NUM": "the spread of", "BIN_COUNT": "the distribution of", "NONE": "",
}

def aggregate_phrase(aggregate: str, name: str) -> str:
    """The aggregate and a column's prose name, joined without saying it twice.

    A readable column name often has the aggregate already in it -- `Total Revenue
    Hours` -- and prefixing that with the same word again gives an axis reading
    "Total Total Revenue Hours". The three places that write this phrase (axis
    title, caption, template title) share one implementation so they cannot disagree
    about what the same figure is called.
    """
    word = AGGREGATE_PHRASE.get(aggregate, aggregate.lower())
    if not word or name.lower().startswith(word.lower()):
        return name
    return f"{word} {name}".strip()


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
class Origin:
    """The pool entry a scenario was drawn from.

    Kept because a batch is a sample of the domain pool and nothing else records
    which part of it was taken: the scenario title is written by the model and says
    nothing about the sub-topic it came from or the tier it was drawn under, so a
    batch could not be described as covering one part of the pool and not another.

    The pool has two axes and both are recorded. `subject` is what the data is about;
    `register` is who published it and for whom, and it is the one that decides
    whether a page reads as a company's own dashboard or as a statistical release --
    which a batch has to be able to say it covers, and `topic` alone cannot.
    """

    domain_id: str = ""
    domain: str = ""            # the sub-topic, the level a scenario is drawn at
    topic: str = ""             # the subject the sub-topic sits under
    subject: str = ""           # what the data is about
    register: str = ""          # who published it and for whom
    complexity_tier: str = ""   # simple | medium | complex


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
    origin: Origin = field(default_factory=Origin)

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
