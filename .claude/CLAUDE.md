# CLAUDE.md

## Project

Chart data generation for **grounded transcription**: synthesize charts where every rendered value carries the pixel box it was drawn in. Output unit is `(key, value, box)`. Ground truth is recorded while drawing — never obtained by annotating finished images.

- Spec: `storyline/parsebench_chart/` — the single source of truth.
- What can be drawn and under what conditions: `storyline/parsebench_chart/chart_types.md`.
- Plan: `IMPL_PLAN.md` — module layout, data interfaces, checklist.
- Running example in every spec doc: hospital ER wait times (3 hospitals × 4 departments × 3 severity levels, 900 rows).

## Pipeline

Six stages, one forward data flow. **LLM appears in 01 and 02 only**, and only ever emits declarations and bindings — never a data value.

| Stage | Package | In → Out | LLM |
|---|---|---|---|
| 01 scenario | `s01_scenario` | domain pool → ScenarioContext | yes |
| 02 facts | `s02_facts` | ScenarioContext → FactTable + TableSchema | yes: writes the generating script and binds each intent to columns |
| 03 figure | `s03_figure` | table + schema → FigureSpec | no |
| 04 render | `s04_render` | FigureSpec + StyleVector → image + L0/L1 | no |
| 05 record | `s05_record` | RenderOutput → Record (3 layers + `readable`) | no |
| 06 targets | `s06_targets` | Record → training target files | no |

Shared layer: `interfaces/` (the five data interfaces), `registry/` (chart conditions + the enumerator), `common/` (seeds, geometry, cache, llm, dedup).

## How the tricky parts work

- **Feasibility is decided at declaration time.** Structural and semantic conditions depend only on column declarations (`dim` value lists give cardinality; `time` start/end/freq give point counts; `additive` and `ordered` — `None` / `"ordinal"` / `"stage"` — are declared fields). `registry/enumerate.py` is a pure function of the schema — 02 calls it for coverage feedback, 03 calls the same function for the candidate list. Only variance / distinctness / actual cell counts need real data.
- **Intent binding happens in 02**, because that is where columns are defined. 01 writes intents as plain sentences; 02 binds each to `(target columns, view class)`; 03 matches deterministically.
- **03 has no LLM.** Enumerate → project → filter by data conditions → pick (intent figures + rotation-filled extra figures).
- **Record while drawing.** Every mark writes its box, key, and values at the moment it is drawn, using the plotting library's own coordinate transform. Never draw first and parse the image afterwards.
- **Freeze layout.** Figure size, dpi, and the axes rectangle are fixed. Auto-layout moves the plot area afterwards and silently invalidates every recorded box.
- **Readability is decided after rendering** from actual pixel geometry plus the encoding channel (length/position → maybe; angle/area/color → no). Unreadable marks drop out of value targets but stay in localization targets.
- **Three self-checks on the production path** (`s05_record/selfcheck.py`): is there anything inside the box, does the value read back from pixels match, does the answer stay the same under a different style. Failure discards the figure and logs the reason.
- **One coordinate convention**: pixels, origin top-left, `[x0, y0, x1, y1]`, image size recorded alongside.
- **Keys are ordered string tuples** — `("协和", "外科")`. All three record layers join on `(figure_id, panel_id, key)`.

## Code Standards

- **Simple, short, clear** — the minimal implementation that solves the problem. No premature abstraction, no oversized files.
- **One file, one responsibility.** Anything used by two stages lives in `common/`, `registry/`, or `interfaces/`.
- **Extract a helper the second time a pattern repeats**, not the first, never the third.
- **Type hints everywhere**; avoid `Any`. `@dataclass` for every structured object, not loose dicts.
- **Stages talk only through `interfaces/`** — no stage imports another stage's internals.
- **Determinism**: `(input, seed) -> output` bit-for-bit. No global random state, no hidden mutation.
- **Split drawing code by mark shape, not by chart type** — 18 chart types, 6 mark shapes.
- **Atomic grain**: one fact-table row = one event. Aggregation happens only in the 03 projection.

## Don'ts

- Don't mention chart types in 01 — scenarios come from the domain, not from visualization templates.
- Don't aggregate at generation time.
- Don't let the LLM judge feasibility; don't reintroduce an LLM call into 03.
- Don't re-render. If a value can't be read off the image, drop it from the value targets.
- Don't add a second plotting backend before the style ablation demands it.
- Don't write ground truth that wasn't recorded during drawing.
- Don't change a data interface without also updating its sample in `tests/samples/` and its `schema_version`.
- Don't describe changes relative to an earlier version of the spec — the spec states only what is current.

## Scope note on other outputs

The recorded metadata (scenario, fact table, schema, FigureSpec, three record layers, style vector) supports more than the eight training targets: QA pairs, chart code, style-paired samples, multi-figure consistency sets. These are extra export functions over the same records, not extra pipeline runs. QA generation is deliberately out of the current line of work, but the record must keep everything it would need — `key`, aggregated values, row counts, dependency graph.

## Maintenance

`storyline/parsebench_chart/` and the code must stay in sync. Update `IMPL_PLAN.md`'s checklist as work lands, and `README.md` for setup or CLI changes. Keep the hospital ER example consistent across all docs — the numbers in 02/03/04/05/06 are chained.
