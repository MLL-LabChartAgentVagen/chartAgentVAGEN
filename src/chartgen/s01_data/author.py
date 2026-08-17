"""The single model call of the pipeline, and the loop around it.

One call produces three things at once: the scenario prose, the generating script,
and the analysis intents already bound to columns. They are written together
because the script is the formal version of the scenario and the intents point at
the script's columns -- splitting them across calls would put a lossy translation
step in between, with no way back upstream to fix it.

    model     writes scenario prose, generating script, bound intents
    rules     parse -> check intents -> check feasibility -> generate -> check data
              all pass  ->  the scenario is done
              any fails ->  assemble the reason and ask again, up to a retry limit

`compose` is the rules half. It knows nothing about models, so the whole stage can
be exercised from a hand-written answer with no network. When it rejects an answer
it raises `Rejected`, whose message is the feedback text and whose `kind` feeds
the failure-type statistics.

The prompt never names a chart type. Scenarios come from subject matter, not from
a catalogue of visualisations; intents stop at the view class, and which chart
type serves a view class is decided later from the column declarations.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Literal, Protocol, Sequence

from ..common.rng import seed_of
from ..config import Config
from ..interfaces.table import FactTable, TableSchema
from ..registry.charts import FAMILIES
from . import engine, validate
from .declare import run, to_schema
from .expr import DeclarationError
from .pool import TARGET_ROWS, TIERS, Pool, Sampler

#: Why an answer was rejected. Also the key the failure statistics count.
RejectKind = Literal["script", "binding", "feasibility", "structure", "duplicate"]

#: How many intents an answer must carry.
INTENT_RANGE = (2, 4)


class Rejected(DeclarationError):
    """An answer did not pass. `kind` is counted, the message is fed back."""

    def __init__(self, kind: RejectKind, message: str) -> None:
        super().__init__(message)
        self.kind: RejectKind = kind


class Authoring(Protocol):
    def json(self, system: str, user: str, *, schema: dict) -> dict: ...


class Sampling(Protocol):
    def take(self, tier: str | None = None) -> Any: ...


# ---------------------------------------------------------------- the output contract

#: Strict JSON envelope with the script as a string. Missing or mistyped fields
#: are caught before any of this module runs.
SCENARIO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["scenario_title", "data_context", "script", "intents"],
    "properties": {
        "scenario_title": {"type": "string"},
        "data_context": {"type": "string"},
        "script": {"type": "string"},
        "intents": {"type": "array", "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["sentence", "columns", "aggregate", "family"],
            "properties": {
                "sentence": {"type": "string"},
                "columns": {"type": "array", "items": {"type": "string"}},
                "aggregate": {"type": "string"},
                "family": {"type": "string", "enum": list(FAMILIES)},
            }}},
    },
}

SYSTEM = """You are a data modelling expert. Given a domain, you write three
things: a paragraph describing the scenario, a script that generates the data, and
the analysis intents the data was collected to answer.

You produce no data values. You write how the data comes about and what questions
it answers. Reply with JSON matching the schema, no explanation and no code fences."""

#: The six view classes, each with the kind of question it covers. No chart type
#: appears here: which chart serves a view class is decided from the declarations.
VIEW_CLASSES = {
    "comparison": "which is highest, which is lowest, how they rank",
    "trend": "how something moves over time, where it turns",
    "composition": "what share each part holds, how the mix shifts",
    "relation": "whether two metrics move together",
    "distribution": "how spread out values are, whether there are outliers",
    "process": "where the largest drop happens along a sequence of stages",
}

USER = """## Domain

{domain}

Aim for {row_lo}-{row_hi} rows and put that number in `emit(n)`.

## What to write

| Field | Content |
|---|---|
| `scenario_title` | One sentence: the period, the organisations, the analytical focus |
| `data_context` | One paragraph: who collected the data, why, and when |
| `script` | A sequence of the four declaration calls below |
| `intents` | 2-4 analysis intents, each a sentence plus target columns, aggregate and view class |

Write every column name, value, unit, scenario sentence and intent sentence in English.

## The four declaration methods

The script contains only these four calls. No loops, no conditionals, no assignments.

```
dim(name, values, weights=None, parent=None, ordered=None, group=None)
    A category column. `parent` expresses a hierarchy; `weights` is either one
    vector or a distribution per parent value; `ordered` is None, "ordinal" (values
    have a natural order) or "stage" (steps something passes through in sequence);
    `group` names the hierarchy chain, and columns on one chain share a group.
    A child value with weight 0 under a parent value does not occur there, which
    is how a value belonging to exactly one parent is written -- a processing
    center sits in one region, while every hospital has a surgery department.
    Every declared value must still occur under some parent.
time(name, start, end, freq)
    A time column, freq is daily, weekly or monthly. The calendar fields
    day_of_week, month, quarter and is_weekend are derived automatically -- do not
    declare them yourself.
measure(name, expr, unit, additive)
    A numeric column. additive: counts, amounts and durations add up; ratios,
    percentages, temperatures and scores do not.
emit(n)
    Produce n rows.
```

## Expressions

| Part | How to write it |
|---|---|
| Distribution | `gaussian(mu, sigma)` `lognormal(mu, sigma)` `gamma(shape, scale)` `beta(a, b)` `uniform(low, high)` `poisson(lam)` `exponential(scale)` `mixture(p, a, b)` |
| Category effect | `[column=value]` is a 0/1 indicator; `{{"value": number}}[column]` is a lookup, and values containing spaces must be quoted |
| Another column | Write its name. A time column evaluates to days since its start |
| Arithmetic | `+ - * / **`, `clip(x, lo, hi)`, `where(condition, a, b)`, `sin` `cos` `log` `exp` `sqrt` |

Dependencies are read out of the expressions, so do not declare them. Statistical
patterns are part of an expression too: an outlier is a multiplicative conditional
term, a trend break is a piecewise term over time, seasonality is a sine over time.

## Constraints

1. One row is one indivisible event; do not lay out a cross product of categories
2. At least 2 dimension groups and at least 2 numeric columns
3. Dependencies must not form a cycle
4. Every symbol in an expression has an explicit numeric definition
5. Declare each numeric column once; do not patch it with later calls
6. Every numeric column declares a unit and additivity
7. Numbers, entities and time windows stay in plausible real-world ranges
8. Size the table to the columns: pick any two category columns you expect to be
   charted together and make sure `n` gives their cross product at least
   {min_rows_per_cell} rows per cell

## View classes for intents

Each intent says which kind of question it answers. There are six:

{view_classes}

`aggregate` is one of SUM, AVG, MAX, MIN, MEDIAN, COUNT, NONE. Summing a
non-additive measure is never legal. Use NONE for a relation between two numeric
columns.

## Worked example

Input:

{example_domain}

Output:

{example_output}
{feedback}"""

FEEDBACK = """
## The previous answer did not pass

{reason}

Fix it and reply with the complete JSON again."""

#: The subject area of the worked example in the prompt.
EXAMPLE_DOMAIN: dict[str, Any] = {
    "name": "Emergency department operations",
    "topic": "Healthcare",
    "complexity_tier": "medium",
    "typical_entities_hint": ["hospital", "department", "triage level"],
    "typical_metrics_hint": [{"name": "wait_time", "unit": "minutes"}],
    "temporal_granularity_hint": "daily",
}

EXAMPLE_SCRIPT = '''dim("hospital", ["Mercy General", "St. Luke's", "Riverside"],
    weights=[0.40, 0.35, 0.25], group="entity")
dim("department", ["Internal Medicine", "Surgery", "Pediatrics", "Trauma"], parent="hospital",
    weights={"Mercy General": [0.35, 0.25, 0.15, 0.25],
             "St. Luke's": [0.40, 0.20, 0.20, 0.20],
             "Riverside": [0.30, 0.30, 0.15, 0.25]})
dim("severity", ["Minor", "Moderate", "Severe"], weights=[0.50, 0.35, 0.15],
    ordered="ordinal", group="triage")

time("visit_date", start="2024-01-01", end="2024-06-30", freq="daily")

measure("wait_minutes",
        "lognormal(mu = 2.8 + 0.4*[severity=Moderate] + 0.9*[severity=Severe]"
        "             + 0.2*[hospital=Mercy General],"
        "          sigma = 0.35)",
        unit="minutes", additive=True)
measure("cost",
        "wait_minutes * 12 + {Minor: 80, Moderate: 260, Severe: 700}[severity] + gaussian(0, 30)",
        unit="USD", additive=True)
measure("satisfaction",
        "clip(5.2 - wait_minutes / 32 + gaussian(0, 0.3), 1, 5)",
        unit="points", additive=False)

emit(900)
'''

EXAMPLE_OUTPUT: dict[str, Any] = {
    "scenario_title": ("Emergency department visits and wait times at three metro "
                       "hospitals, Jan-Jun 2024"),
    "data_context": ("The county health department compiled per-visit records from three "
                     "hospitals for January through June 2024 to assess a new triage "
                     "diversion policy."),
    "script": EXAMPLE_SCRIPT,
    "intents": [
        {"sentence": "Which hospital and department waits longest",
         "columns": ["hospital", "wait_minutes"], "aggregate": "AVG",
         "family": "comparison"},
        {"sentence": "How wait time moved over the half year",
         "columns": ["visit_date", "wait_minutes"], "aggregate": "AVG", "family": "trend"},
        {"sentence": "Do longer waits go with lower satisfaction",
         "columns": ["wait_minutes", "satisfaction"], "aggregate": "NONE",
         "family": "relation"},
    ],
}


def _json(value: Any) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def user_prompt(domain: dict[str, Any], row_range: tuple[int, int],
                feedback: str | None = None) -> str:
    """The user message for one call. A non-empty `feedback` makes it a retry."""
    return USER.format(
        domain=_json(domain),
        row_lo=row_range[0], row_hi=row_range[1],
        min_rows_per_cell=validate.MIN_ROWS_PER_CELL,
        view_classes="\n".join(f"- `{k}`: {v}" for k, v in VIEW_CLASSES.items()),
        example_domain=_json(EXAMPLE_DOMAIN),
        example_output=_json(EXAMPLE_OUTPUT),
        feedback=FEEDBACK.format(reason=feedback) if feedback else "",
    )


# ---------------------------------------------------------------- the rules half

def compose(payload: dict[str, Any], *, scenario_id: str, seed: int,
            config: Config) -> tuple[FactTable, TableSchema]:
    """One answer to a fact table and a schema. Raises `Rejected` if it fails a check."""
    try:
        script = run(str(payload["script"]))
    except DeclarationError as exc:
        raise Rejected("script", str(exc)) from exc

    schema = to_schema(script, scenario_id=scenario_id,
                       title=str(payload["scenario_title"]),
                       context=str(payload["data_context"]))
    raw_intents = payload.get("intents") or []
    lo, hi = INTENT_RANGE
    if not lo <= len(raw_intents) <= hi:
        raise Rejected("binding",
                       f"write {lo}-{hi} analysis intents, got {len(raw_intents)}")
    try:
        schema = replace(schema, intents=validate.intents(raw_intents, schema))
    except DeclarationError as exc:
        raise Rejected("binding", str(exc)) from exc

    min_families = int(config.get("data.min_nonempty_families", validate.MIN_FAMILIES))
    drawable = validate.feasibility(schema, max_tier=int(config.get("scale.max_tier", 3)),
                                    min_families=min_families)
    if not drawable.ok(min_families):
        raise Rejected("feasibility", drawable.feedback())

    try:
        df = engine.generate(script, seed)
    except DeclarationError as exc:
        raise Rejected("script", str(exc)) from exc

    failures = validate.structural(
        df, script, tolerance=float(config.get("data.row_tolerance", validate.ROW_TOLERANCE)))
    if failures:
        raise Rejected("structure", "\n".join(f.message for f in failures))

    return FactTable(scenario_id, df), replace(schema, n_rows=len(df))


# ---------------------------------------------------------------- the call and the loop

def build_scenario(scenario_id: str, seed: int, config: Config, *,
                   llm: Authoring | None = None, domain: dict[str, Any] | None = None,
                   sampler: Sampling | None = None,
                   is_duplicate: Callable[[str], bool] | None = None,
                   log: list[Rejected] | None = None) -> tuple[FactTable, TableSchema]:
    """One call per scenario; on rejection ask again with the reason attached.

    `is_duplicate` decides whether a scenario is too close to one already seen. It
    is given the title rather than the paragraph: a title is short and specific,
    which is what a cheap similarity judge can separate. A hit does not count as a
    retry -- it draws a different sub-topic and starts over, because asking about the
    same subject area again would only produce the same scenario.
    """
    llm = llm or _default_llm(config)
    retries = int(config.get("llm.max_retries", 3))
    feedback: str | None = None
    last: Rejected | None = None

    for _ in range(retries + 1):
        if domain is None:
            sampler = sampler or _default_sampler(config, scenario_id)
            domain = _next_domain(sampler, _tier_of(scenario_id, seed))
        payload = llm.json(SYSTEM, user_prompt(domain, _row_range(domain), feedback),
                           schema=SCENARIO_SCHEMA)

        if is_duplicate is not None and is_duplicate(str(payload.get("scenario_title", ""))):
            last = Rejected("duplicate",
                            "the scenario is too close to one already generated; "
                            "drawing another sub-topic")
            _note(log, last)
            domain, feedback = None, None
            continue
        try:
            return compose(payload, scenario_id=scenario_id, seed=seed, config=config)
        except Rejected as exc:
            last, feedback = exc, str(exc)
            _note(log, exc)

    raise last or Rejected("script", f"no usable answer in {retries + 1} attempts")


def failure_counts(log: Sequence[Rejected]) -> dict[str, int]:
    """How often each rejection kind happened. A frequent kind belongs in the prompt."""
    out: dict[str, int] = {}
    for item in log:
        out[item.kind] = out.get(item.kind, 0) + 1
    return out


def _note(log: list[Rejected] | None, exc: Rejected) -> None:
    if log is not None:
        log.append(exc)


def _row_range(domain: dict[str, Any]) -> tuple[int, int]:
    return TARGET_ROWS.get(domain.get("complexity_tier", "medium"), (500, 1000))


def _next_domain(sampler: Sampling, tier: str) -> dict[str, Any]:
    picked = sampler.take(tier)
    return picked if isinstance(picked, dict) else picked.to_dict()


def _tier_of(scenario_id: str, seed: int) -> str:
    """Which complexity tier a scenario draws from. Fixed by the scenario, so a
    batch spreads over the three tiers instead of taking the same one every time."""
    return TIERS[seed_of(seed, scenario_id, "tier") % len(TIERS)]


def _default_sampler(config: Config, scenario_id: str) -> Sampling:
    """One sampler per scenario, seeded with the scenario it draws for.

    A sampler holds what it has already handed out, so it must outlive the retry
    loop: a scenario rejected as a near-duplicate has to draw a different
    sub-topic, and a fresh sampler would hand back the one just rejected. The
    scenario identifier goes into the seed for the same reason -- without it every
    scenario in a batch starts from the same draw.
    """
    path = Path(str(config.get("data.pool_path", "data/domains/pool.json")))
    if not path.exists():
        raise FileNotFoundError(
            f"no domain pool at {path}. Build one: python -m chartgen.cli pool --out {path}")
    return Sampler(Pool.load(path), seed_of(int(config.get("root_seed", 0)), scenario_id))


def _default_llm(config: Config) -> Authoring:
    from llmkit import LLM

    return LLM(model=str(config.get("llm.model")),
               max_tokens=int(config.get("llm.max_tokens", 8000)),
               cache_dir=config.get("llm.cache_dir"))
