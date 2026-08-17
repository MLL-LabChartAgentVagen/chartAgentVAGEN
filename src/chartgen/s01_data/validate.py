"""Everything that can reject a set of declarations, and the text that explains why.

Three checks live here, all of which produce feedback the model can act on:

    feasibility     which chart families this schema can draw at all. Reads only
                    the declarations, so it runs before any row is generated --
                    which matters because the model that wrote the script cannot
                    be reached again once this stage is over
    intents         each analysis intent names columns that exist, an aggregate
                    the measure allows, and one of the six view classes
    structural      after generation: row count, distinct values per category
                    column, and that every numeric column is finite and varies

The distinct-value check is what makes the feasibility result trustworthy: family
membership is decided from declared cardinalities, so the generated data has to
match them.

`Failure.kind` is also a statistic. Counting failure kinds across runs shows which
constraint the model gets wrong most often, and that constraint belongs in the
prompt rather than in a higher retry limit.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Literal, Sequence

import numpy as np
import pandas as pd

from ..interfaces.table import (
    AGG_ADDITIVE, AGG_NON_ADDITIVE, Aggregate, IntentBinding, TableSchema,
)
from ..registry import conditions
from ..registry.charts import FAMILIES
from .declare import Script, calendar_values
from .expr import DeclarationError

FailureKind = Literal["rows", "cardinality", "measure"]

#: How far the generated row count may drift from the count the script asked for.
ROW_TOLERANCE = 0.10

#: How many chart families must be non-empty for a schema to be worth using.
MIN_FAMILIES = 3

#: Category cardinality a plain one-dimension comparison chart accepts.
CARD_RANGE = (3, 30)

#: Rows a two-dimension cross needs per cell before grouped and stacked charts
#: carry any information.
MIN_ROWS_PER_CELL = 5

#: Cell counts worth screening: below this a cross is not a chart, above it the
#: chart is unreadable.
CELL_RANGE = (6, 100)

#: The aggregate that counts rows instead of reading a measure.
NO_MEASURE_AGGREGATE: Aggregate = "COUNT"

#: Aggregates that read a measure and return one number per group.
SCALAR_AGGREGATES = ("SUM", "AVG", "MAX", "MIN", "MEDIAN")

NO_ADDITIVE = (
    "No measure is additive, so a composition chart can only fall back to counting "
    "rows and no share of an amount or a duration can be drawn. Add a count, amount "
    "or duration measure and declare additive=True.")
NO_STAGE = (
    'No dimension is declared ordered="stage", so no process chart can be drawn. '
    "If this scenario has genuine sequential stages, declare that dimension as a "
    "stage; if it does not, leave it out rather than inventing one.")
BAD_CARDINALITY = (
    f"Every category column falls outside {CARD_RANGE[0]}-{CARD_RANGE[1]} distinct "
    "values, so no comparison chart can be drawn. Adjust how many values they take.")


# ---------------------------------------------------------------- feasibility

@dataclass(frozen=True)
class Feasibility:
    """Which families are non-empty, and what is missing when they are not."""

    families: dict[str, bool]
    gaps: tuple[str, ...] = ()

    @property
    def nonempty(self) -> int:
        return sum(self.families.values())

    @property
    def empty_families(self) -> tuple[str, ...]:
        return tuple(f for f, ok in self.families.items() if not ok)

    def ok(self, min_families: int = MIN_FAMILIES) -> bool:
        return self.nonempty >= min_families

    def feedback(self) -> str:
        return "\n".join(self.gaps)


def feasibility(schema: TableSchema, *, max_tier: int = 3,
                min_families: int = MIN_FAMILIES) -> Feasibility:
    """Decide per family whether anything is drawable. Reads declarations only."""
    families = conditions.coverage(schema, max_tier)
    return Feasibility(families, _gaps(schema, families, min_families))


def _gaps(schema: TableSchema, families: dict[str, bool], min_families: int) -> tuple[str, ...]:
    out: list[str] = []
    if not any(c.additive for c in schema.measures):
        out.append(NO_ADDITIVE)
    if not any(c.ordered == "stage" for c in schema.categories):
        out.append(NO_STAGE)
    if not any(CARD_RANGE[0] <= c.cardinality <= CARD_RANGE[1] for c in schema.categories):
        out.append(BAD_CARDINALITY)
    if thin := density_gap(schema):
        out.append(thin)
    nonempty = sum(families.values())
    if nonempty < min_families:
        out.append(
            f"Only {nonempty} of the six chart families are non-empty (empty: "
            f"{[f for f, ok in families.items() if not ok]}), below the threshold of "
            f"{min_families}: this schema would yield very few figures per scenario.")
    return tuple(out)


def expected_rows_per_cell(schema: TableSchema, columns: Sequence[str]) -> float:
    """Rows per cell if the table were split by these columns.

    A declaration-time screen only: coefficient of variation and distinctness need
    real values, but how thinly the rows spread over a cross product follows from
    the row count and the declared cardinalities.
    """
    cells = 1
    for name in columns:
        cells *= schema.column(name).cardinality
    return schema.n_rows / cells if cells else 0.0


def densest_cross(schema: TableSchema) -> tuple[tuple[str, str] | None, float]:
    """The two category columns whose cross has the most rows per cell.

    Only crosses that could actually become a chart are considered. If even the
    best one is thin, every two-dimension chart in this scenario is thin.
    """
    best: tuple[str, str] | None = None
    best_density = 0.0
    for a, b in combinations(schema.categories, 2):
        if a.derived_from and b.derived_from == a.derived_from:
            continue                      # two calendar fields off one time column
        cells = a.cardinality * b.cardinality
        if not CELL_RANGE[0] <= cells <= CELL_RANGE[1]:
            continue
        density = schema.n_rows / cells
        if density > best_density:
            best, best_density = (a.name, b.name), density
    return best, best_density


def density_gap(schema: TableSchema) -> str:
    """Feedback text when the table is too thin for any two-dimension chart."""
    pair, density = densest_cross(schema)
    if pair is None or density >= MIN_ROWS_PER_CELL:
        return ""
    cells = schema.n_rows / density
    return (f"With {schema.n_rows} rows the table is too thin to cross two category "
            f"columns: the densest pair ({pair[0]} x {pair[1]}) leaves {density:.1f} rows "
            f"per cell, below the {MIN_ROWS_PER_CELL} a grouped or stacked chart needs. "
            f"Raise the row count to about {int(cells * MIN_ROWS_PER_CELL)}, or declare "
            "fewer values per column.")


# ---------------------------------------------------------------- intent bindings

def intents(raw: Sequence[dict[str, Any]], schema: TableSchema) -> tuple[IntentBinding, ...]:
    """Check and build the intent bindings: columns exist, aggregate is legal, family is one of six."""
    if not raw:
        raise DeclarationError("at least one analysis intent is required")
    return tuple(_intent(i, item, schema) for i, item in enumerate(raw))


def _intent(index: int, item: dict[str, Any], schema: TableSchema) -> IntentBinding:
    where = f"intent {index + 1}"
    columns = tuple(str(c) for c in item.get("columns", ()))
    if not columns:
        raise DeclarationError(f"{where} binds no columns")
    for name in columns:
        if not schema.has(name):
            raise DeclarationError(f"{where} binds `{name}`, which is not declared")

    family = item.get("family")
    if family not in FAMILIES:
        raise DeclarationError(
            f"{where} has family {item.get('family')!r}; it must be one of {list(FAMILIES)}")

    aggregate = str(item.get("aggregate", "NONE")).upper()
    _aggregate(where, aggregate, columns, schema)
    return IntentBinding(index, str(item.get("sentence", "")).strip(), columns,
                         aggregate, family)  # type: ignore[arg-type]


def _aggregate(where: str, aggregate: str, columns: Sequence[str],
               schema: TableSchema) -> None:
    measures = [schema.column(c) for c in columns if schema.column(c).kind == "measure"]
    if aggregate == NO_MEASURE_AGGREGATE:
        if measures:
            raise DeclarationError(f"{where} counts rows, so it must not bind a measure")
        return
    if not measures:
        raise DeclarationError(
            f"{where} aggregates with {aggregate} but binds no measure "
            "(use COUNT to count rows)")
    if aggregate in SCALAR_AGGREGATES:
        for col in measures:
            legal = AGG_ADDITIVE if col.additive else AGG_NON_ADDITIVE
            if aggregate not in legal:
                kind = "additive" if col.additive else "non-additive"
                raise DeclarationError(
                    f"{where} applies {aggregate} to the {kind} measure `{col.name}`; "
                    f"it allows {list(legal)}")
        return
    if aggregate in ("NONE", "FIVE_NUM", "BIN_COUNT"):
        return
    raise DeclarationError(f"{where} has aggregate {aggregate!r}, which is not a legal aggregate")


# ---------------------------------------------------------------- generated data

@dataclass(frozen=True)
class Failure:
    kind: FailureKind
    message: str


def structural(df: pd.DataFrame, script: Script, *,
               tolerance: float = ROW_TOLERANCE) -> tuple[Failure, ...]:
    """Check the generated table against its declarations."""
    return (*_rows(df, script, tolerance), *_cardinality(df, script), *_measures(df, script))


def _rows(df: pd.DataFrame, script: Script, tolerance: float) -> list[Failure]:
    target = script.n_rows
    if abs(len(df) - target) > tolerance * target:
        return [Failure("rows", f"generated {len(df)} rows, the script asked for {target}, "
                                f"which is outside +/-{tolerance:.0%}")]
    return []


def _cardinality(df: pd.DataFrame, script: Script) -> list[Failure]:
    declared: dict[str, tuple[str, ...]] = {d.name: d.values for d in script.dims}
    if script.time is not None:
        declared |= calendar_values(script.time)

    out: list[Failure] = []
    for name, values in declared.items():
        actual = set(df[name].unique())
        if missing := sorted(set(values) - actual):
            out.append(Failure("cardinality",
                               f"`{name}` declares {len(values)} values but only "
                               f"{len(actual)} appear; missing {', '.join(missing)}"))
        elif extra := sorted(actual - set(values)):
            out.append(Failure("cardinality", f"`{name}` produced undeclared values: {extra}"))
    return out


def _measures(df: pd.DataFrame, script: Script) -> list[Failure]:
    out: list[Failure] = []
    for m in script.measures:
        col = df[m.name]
        if col.isna().any() or not np.isfinite(col.to_numpy(dtype=float)).all():
            out.append(Failure("measure", f"`{m.name}` holds nulls or non-finite values"))
        elif col.nunique() <= 1:
            out.append(Failure("measure",
                               f"`{m.name}` is the constant {col.iloc[0]}; nothing can be drawn from it"))
    return out
