"""The four declaration methods, and turning a set of declarations into a schema.

A generating script is a sequence of four calls and nothing else -- no loops, no
conditionals, no assignments:

    dim(name, values, weights, parent, ordered, group)   a category column
    time(name, start, end, freq)                         a time column
    measure(name, expr, unit, additive)                  a numeric column
    emit(n)                                              produce n rows

`run` executes such a script in an empty namespace and collects the declarations,
checking each call as it arrives. Checks come in two layers: per-call arguments
are checked where the call happens (how many values a dimension has, whether the
dates parse), and whole-script constraints are checked after `emit` (at least two
dimension groups, at least two numeric columns, no column may take a derived
calendar name).

`to_schema` needs no data at all: cardinality comes from the length of a value
list and from the start/end/freq of the time column. That is what lets the
feasibility check run before a single row exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterator, Sequence

from ..interfaces.table import (
    Column, DimGroup, Freq, IntentBinding, Ordered, TableSchema,
)
from .expr import DeclarationError, edges, parse

#: Calendar fields derived from a time column. No other column may take these names.
DERIVED: tuple[str, ...] = ("day_of_week", "month", "quarter", "is_weekend")

#: Dimension group that holds the time column and its derived calendar fields.
CALENDAR = "calendar"

WEEKDAYS: tuple[str, ...] = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

FREQS: tuple[Freq, ...] = ("daily", "weekly", "monthly")

ORDERED: tuple[Ordered | None, ...] = (None, "ordinal", "stage")

MIN_GROUPS = 2
MIN_MEASURES = 2

Weights = tuple[float, ...] | dict[str, tuple[float, ...]] | None


@dataclass(frozen=True)
class DimDecl:
    name: str
    values: tuple[str, ...]
    weights: Weights = None
    parent: str | None = None
    ordered: Ordered | None = None
    group: str = ""

    @property
    def cardinality(self) -> int:
        return len(self.values)


@dataclass(frozen=True)
class TimeDecl:
    name: str
    start: str
    end: str
    freq: Freq

    def points(self) -> tuple[date, ...]:
        """Every point on the time axis. Cardinality and the derived calendar
        fields are computed from this, so no data is needed."""
        lo, hi = date.fromisoformat(self.start), date.fromisoformat(self.end)
        if self.freq == "daily":
            return tuple(lo + timedelta(days=i) for i in range((hi - lo).days + 1))
        if self.freq == "weekly":
            first = lo - timedelta(days=lo.weekday())
            n = ((hi - first).days // 7) + 1
            return tuple(first + timedelta(weeks=i) for i in range(n))
        months = (hi.year - lo.year) * 12 + hi.month - lo.month
        return tuple(date(lo.year + (lo.month - 1 + i) // 12,
                          (lo.month - 1 + i) % 12 + 1, 1) for i in range(months + 1))


@dataclass(frozen=True)
class MeasureDecl:
    name: str
    expr: str
    unit: str
    additive: bool


@dataclass(frozen=True)
class Script:
    """A script that has finished executing. No data exists yet."""

    dims: tuple[DimDecl, ...]
    time: TimeDecl | None
    measures: tuple[MeasureDecl, ...]
    n_rows: int

    def dim(self, name: str) -> DimDecl:
        for d in self.dims:
            if d.name == name:
                return d
        raise KeyError(f"no such dimension: {name}")

    def children_of(self, name: str) -> tuple[DimDecl, ...]:
        return tuple(d for d in self.dims if d.parent == name)


# ---------------------------------------------------------------- execution

def run(text: str) -> Script:
    """Execute a declaration script in an isolated namespace.

    Failures carry the line number: when the text is fed back to the model,
    "line 4" is worth more than a stack trace.
    """
    collector = _Collector()
    namespace: dict[str, Any] = {
        "__builtins__": {},
        "dim": collector.dim, "time": collector.time,
        "measure": collector.measure, "emit": collector.emit,
    }
    try:
        exec(compile(text, "<script>", "exec"), namespace)   # noqa: S102 -- no builtins
    except DeclarationError as exc:
        raise DeclarationError(f"{_where(exc)}{exc}") from exc
    except Exception as exc:  # noqa: BLE001 -- every failure must become feedback text
        raise DeclarationError(
            f"{_where(exc)}script failed: {type(exc).__name__}: {exc}") from exc
    return collector.finish()


def _where(exc: BaseException) -> str:
    """Which line of the script failed."""
    tb, line = exc.__traceback__, None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == "<script>":
            line = tb.tb_lineno
        tb = tb.tb_next
    return f"line {line}: " if line else ""


class _Collector:
    """Receives the four declaration calls and checks each one on arrival."""

    def __init__(self) -> None:
        self.dims: list[DimDecl] = []
        self.time_decl: TimeDecl | None = None
        self.measures: list[MeasureDecl] = []
        self.n_rows: int | None = None

    # ---- the four methods

    def dim(self, name: str, values: Sequence[Any], weights: Any = None,
            parent: str | None = None, ordered: str | None = None,
            group: str | None = None) -> None:
        self._fresh(name)
        vals = tuple(str(v) for v in values)
        if len(vals) < 2:
            raise DeclarationError(f"`{name}` needs at least 2 values, got {len(vals)}")
        if len(set(vals)) != len(vals):
            raise DeclarationError(f"`{name}` has repeated values: {vals}")
        if ordered not in ORDERED:
            raise DeclarationError(
                f'`{name}` takes ordered=None, "ordinal" or "stage", got {ordered!r}')
        if parent is not None and parent not in {d.name for d in self.dims}:
            raise DeclarationError(f"`{name}` has parent `{parent}`, which is not declared")
        self.dims.append(DimDecl(name, vals, self._weights(name, vals, weights, parent),
                                 parent, ordered,  # type: ignore[arg-type]
                                 group or self._default_group(name, parent)))

    def time(self, name: str, start: str, end: str, freq: str = "daily") -> None:
        self._fresh(name)
        if self.time_decl is not None:
            raise DeclarationError(
                f"time column `{self.time_decl.name}` is already declared; only one is allowed")
        if freq not in FREQS:
            raise DeclarationError(f"`{name}` takes freq in {FREQS}, got {freq!r}")
        try:
            lo, hi = date.fromisoformat(str(start)), date.fromisoformat(str(end))
        except ValueError as exc:
            raise DeclarationError(f"`{name}` needs dates as YYYY-MM-DD: {exc}") from exc
        if hi <= lo:
            raise DeclarationError(f"`{name}` has end {end} at or before start {start}")
        self.time_decl = TimeDecl(name, lo.isoformat(), hi.isoformat(), freq)  # type: ignore[arg-type]

    def measure(self, name: str, expr: str, unit: str | None = None,
                additive: bool | None = None) -> None:
        self._fresh(name)
        if not isinstance(unit, str) or not unit.strip():
            raise DeclarationError(f"`{name}` must declare a unit")
        if not isinstance(additive, bool):
            raise DeclarationError(
                f"`{name}` must declare additive=True or False (counts, amounts and "
                "durations add up; ratios, percentages and scores do not)")
        parse(expr)                                   # parsed at declaration time
        self.measures.append(MeasureDecl(name, expr, unit.strip(), additive))

    def emit(self, n: int) -> None:
        if self.n_rows is not None:
            raise DeclarationError("emit may be called only once")
        if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
            raise DeclarationError(f"emit takes a positive row count, got {n!r}")
        self.n_rows = n

    # ---- whole-script constraints

    def finish(self) -> Script:
        if self.n_rows is None:
            raise DeclarationError("the script must end with emit(n)")
        if self.time_decl is not None:
            taken = sorted({d.name for d in self.dims} & set(DERIVED))
            if taken:
                raise DeclarationError(
                    f"{taken} are derived from the time column; pick other names")
        if len(self.measures) < MIN_MEASURES:
            raise DeclarationError(
                f"at least {MIN_MEASURES} numeric columns are required, "
                f"got {len(self.measures)}")
        groups = {d.group for d in self.dims}
        if len(groups) < MIN_GROUPS:
            raise DeclarationError(
                f"at least {MIN_GROUPS} dimension groups are required, got "
                f"{sorted(groups) or 'none'} (columns on one hierarchy chain count as "
                "one group; name a chain with group=)")
        return Script(tuple(self.dims), self.time_decl, tuple(self.measures), self.n_rows)

    # ---- internals

    def _fresh(self, name: str) -> None:
        if not isinstance(name, str) or not name.isidentifier():
            raise DeclarationError(f"a column name must be an identifier, got {name!r}")
        if name in self._names():
            raise DeclarationError(f"`{name}` is already declared; declare each column once")

    def _names(self) -> set[str]:
        return ({d.name for d in self.dims} | {m.name for m in self.measures}
                | ({self.time_decl.name} if self.time_decl else set()))

    def _default_group(self, name: str, parent: str | None) -> str:
        """With no group given, take the root of this hierarchy chain."""
        return self.dim_of(parent).group if parent else name

    def dim_of(self, name: str) -> DimDecl:
        return next(d for d in self.dims if d.name == name)

    def _weights(self, name: str, values: tuple[str, ...], weights: Any,
                 parent: str | None) -> Weights:
        if weights is None:
            return None
        if isinstance(weights, dict):
            if parent is None:
                raise DeclarationError(
                    f"`{name}` gives weights per parent value but declares no parent")
            expected = set(self.dim_of(parent).values)
            if missing := sorted(expected - set(weights)):
                raise DeclarationError(
                    f"the weights of `{name}` are missing values of `{parent}`: "
                    f"{', '.join(missing)}")
            if extra := sorted(set(weights) - expected):
                raise DeclarationError(
                    f"the weights of `{name}` name parent values that do not exist: {extra}")
            return {k: self._vector(name, values, weights[k]) for k in sorted(weights)}
        return self._vector(name, values, weights)

    @staticmethod
    def _vector(name: str, values: tuple[str, ...], raw: Any) -> tuple[float, ...]:
        try:
            vec = tuple(float(w) for w in raw)
        except (TypeError, ValueError) as exc:
            raise DeclarationError(f"the weights of `{name}` must be numbers: {raw!r}") from exc
        if len(vec) != len(values):
            raise DeclarationError(
                f"`{name}` has {len(values)} values but {len(vec)} weights")
        if any(w < 0 for w in vec) or sum(vec) <= 0:
            raise DeclarationError(
                f"the weights of `{name}` must be non-negative and not all zero: {vec}")
        return vec


# ---------------------------------------------------------------- declarations to schema

def to_schema(script: Script, *, scenario_id: str, title: str, context: str,
              intents: Sequence[IntentBinding] = (), n_rows: int | None = None) -> TableSchema:
    """Declarations to a table schema. Needs no data: every cardinality is declared."""
    columns = tuple(_columns(script, n_rows if n_rows is not None else script.n_rows))
    return TableSchema(
        scenario_id=scenario_id,
        scenario_title=title,
        data_context=context,
        columns=columns,
        groups=_groups(columns),
        dependencies=edges(tuple((m.name, m.expr) for m in script.measures)),
        intents=tuple(intents),
        n_rows=n_rows if n_rows is not None else script.n_rows,
    )


def _columns(script: Script, n_rows: int) -> Iterator[Column]:
    for d in script.dims:
        yield Column(d.name, "category", d.cardinality, group=d.group, parent=d.parent,
                     ordered=d.ordered, values=d.values)
    if script.time is not None:
        points = script.time.points()
        yield Column(script.time.name, "time", len(points), group=CALENDAR,
                     freq=script.time.freq, start=script.time.start, end=script.time.end)
        for name, values in calendar_values(points).items():
            yield Column(name, "category", len(values), group=CALENDAR, ordered="ordinal",
                         values=values, derived_from=script.time.name)
    for m in script.measures:
        yield Column(m.name, "measure", n_rows, unit=m.unit, additive=m.additive)


def calendar_values(points: Sequence[date]) -> dict[str, tuple[str, ...]]:
    """The values each derived calendar field takes, in time order.

    They are computed from the set of time points, so a cardinality declared here
    always matches the data that gets generated. A field with a single value is
    dropped: on a weekly axis every point is a Monday, which makes `day_of_week`
    and `is_weekend` constant and useless. Schema building, generation and the
    structural check all read this one function, so they cannot disagree.
    """
    out: dict[str, list[str]] = {name: [] for name in DERIVED}
    for name, value in zip(DERIVED * len(points),
                           (v for p in points for v in calendar_of(p))):
        if value not in out[name]:
            out[name].append(value)
    order = {"day_of_week": WEEKDAYS}
    return {name: tuple(sorted(vals, key=order[name].index) if name in order else vals)
            for name, vals in out.items() if len(vals) >= 2}


def calendar_of(day: date) -> tuple[str, str, str, str]:
    """The four derived calendar values of one day, in `DERIVED` order."""
    return (WEEKDAYS[day.weekday()], f"{day.year}-{day.month:02d}",
            f"{day.year}-Q{(day.month - 1) // 3 + 1}",
            "Yes" if day.weekday() >= 5 else "No")


def _groups(columns: Sequence[Column]) -> tuple[DimGroup, ...]:
    names: list[str] = []
    members: dict[str, list[str]] = {}
    for c in columns:
        if c.group is None:
            continue
        if c.group not in members:
            names.append(c.group)
            members[c.group] = []
        members[c.group].append(c.name)
    return tuple(DimGroup(n, tuple(members[n])) for n in names)
