# CLAUDE.md

## Project

Chart data generation for **grounded transcription**: synthesize charts where every rendered value carries the pixel box it was drawn in. Output unit is `(key, value, box)`. Ground truth is recorded while drawing — never obtained by annotating finished images.

- Spec: `storyline/parsebench_chart/` — the single source of truth.
- What can be drawn and under what conditions: `storyline/parsebench_chart/chart_types.md`.
- Plan: `IMPL_PLAN.md` — module layout, data interfaces, checklist.
- Running example in every spec doc: hospital ER wait times (3 hospitals × 4 departments × 3 severity levels, 900 rows).

## Pipeline

Five stages, one forward data flow. **The whole pipeline makes exactly one LLM call**, in 01, and it emits only declarations and bindings, never a data value. Everything else is program.

Each spec doc opens with a worked example and tags every step `[LLM]` or `[规则]`; keep that convention when editing them.

| Stage | Package | In → Out | LLM |
|---|---|---|---|
| 01 data | `s01_data` | domain pool → FactTable + TableSchema | yes, one call: writes the scenario prose, the generating script, and the intents already bound to columns. Parsing, enumeration, the coverage check, execution and the structural check are all program |
| 02 figure | `s02_figure` | table + schema → FigureSpec | no |
| 03 render | `s03_render` | FigureSpec + StyleVector → image + L0/L1 | no |
| 04 record | `s04_record` | RenderOutput → Record (3 layers + `readable`) | no |
| 05 output | `s05_output` | Record → training target files | no |

Shared layer: `interfaces/` (the six data interfaces), `registry/` (chart conditions + the enumerator), `common/` (seeds, geometry, pixel readback, cache, llm, dedup).

## How the tricky parts work

- **One LLM call, three outputs.** Scenario prose, the declaration script, and the intents — each intent carrying its target columns, aggregate, and view class — all come out of the same call. The script *is* the formalized scenario, so splitting this into two calls would insert a lossy JSON layer (hierarchy, orderedness, units and additivity are not explicit in prose) with no feedback path back upstream. Because the columns and the intents are written together, intent binding holds by construction rather than by inference.
- **Feasibility is decided at declaration time.** Structural and semantic conditions depend only on column declarations (`dim` value lists give cardinality; `time` start/end/freq give point counts; `additive` and `ordered` — `None` / `"ordinal"` / `"stage"` — are declared fields). `registry/enumerate.py` is a pure function of the schema — 01 calls it for coverage feedback, 02 calls the same function for the candidate list. Only variance / distinctness / actual cell counts need real data.
- **02 has no LLM.** Enumerate → project → filter by data conditions → pair → pick and compose. **LLM only ever defines; it never selects** — it writes a family and target columns and never sees the candidate list. The condition table then fixes the type inside that family and a deterministic order breaks ties. Be precise about the consequence: an intent's view class *is* a chart family, so the 3 main figures per scenario have their family set by model preference (which is the point — those are the figures an analyst would draw). Type coverage is carried by the 5 rotation and multi-panel figures.
- **Row filters stay out of the enumeration cross product.** They serve exactly one pairing relationship (time comparison), so multiplying every candidate by a window count is waste. `s02_figure/pair.py` slices the complementary halves off the anchor view on demand.
- **Enumeration runs in both 01 and 02, on purpose.** Same pure function. 01 keeps only the summary — candidate count, families covered, families missing — to build the retry feedback, because only 01 can edit the script and the pipeline is one-way. 02 recomputes the list. The list is fully derivable from TableSchema, so putting it on the interface would be caching a derived value.
- **Truncate by rotation over (column, aggregate), never by prefix.** A prefix cut concentrates the surviving views on the first-declared columns and the first aggregate in order. Rotation is still deterministic. The cap exists to bound projection cost and figure-selection diversity, not because enumeration is expensive — it never touches data.
- **Projection has four shapes, not one.** Grouped scalar (bar family, line, area, pie, heatmap, treemap, compound, waterfall, funnel), grouped five-number (box, violin), binned count (histogram), and **per-row with no grouping** (scatter, bubble). Scatter and bubble need deterministic down-sampling to the type's point cap, and their L2 degenerates: `rows` is 1 per mark, and histogram's `rows` equals its `count`. The aggregate set follows the shape — `FIVE_NUM`, `BIN_COUNT`, `NONE` are not SUM/AVG/COUNT.
- **Multi-panel figures are composed by rule** in `s02_figure/pair.py`, from five relationships that are pure ViewSpec field comparisons: drill-down (group keys are a subset), dual-metric (same keys, different measure), orthogonal slice (same measure, disjoint keys), time comparison (complementary row filters), part-whole (composition family + comparison family). The relationship determines the layout and what is shared. This is not optional decoration: `applies_to_panels` on legend entries — one of the eight training targets — is trivial on single-panel figures, so without multi-panel composition that target is always empty.
- **Record while drawing.** Every mark writes its box, key, and values at the moment it is drawn, using the plotting library's own coordinate transform. Never draw first and parse the image afterwards.
- **Freeze layout.** Figure size, dpi, and the axes rectangle are fixed. Auto-layout moves the plot area afterwards and silently invalidates every recorded box.
- **Readability is decided after rendering** from actual pixel geometry plus the encoding channel (length/position → maybe; angle/area/color → no). The rule is defined once, in `chart_types.md` §4. Unreadable marks drop out of value targets but stay in localization targets.
- **Three self-checks on the production path** (`s04_record/selfcheck.py`): is there anything inside the box, does the value read back from pixels match, does the answer stay the same under a different style. Failure discards the figure and logs the reason. The third one needs no extra render — it consumes the style-paired versions that are a product in their own right.
- **The first two self-checks are also the RL reward.** They need only the image and the claimed `(value, box)`, not ground truth. `common/readback.py` holds the one implementation; `s04_record/selfcheck.py` feeds it the renderer's record, `s05_output/verify.py` feeds it the model's output.
- **Visual variants live in the style vector, not the type table.** Two "types" whose four condition columns, mark shape and value dict are identical (solid pie vs. donut) occupy one row in `registry/charts.py`; the difference is a `StyleVector` field.
- **One coordinate convention**: pixels, origin top-left, `[x0, y0, x1, y1]`, image size recorded alongside.
- **Keys are ordered string tuples** — `("协和", "外科")`. All three record layers join on `(figure_id, panel_id, key)`.

## Code Standards

- **Simple, short, clear** — the minimal implementation that solves the problem. No premature abstraction, no oversized files.
- **One file, one responsibility.** Anything used by two stages lives in `common/`, `registry/`, or `interfaces/`.
- **Extract a helper the second time a pattern repeats**, not the first, never the third.
- **Type hints everywhere**; avoid `Any`. `@dataclass` for every structured object, not loose dicts.
- **Stages talk only through `interfaces/`** — no stage imports another stage's internals.
- **Determinism**: `(input, seed) -> output` bit-for-bit. No global random state, no hidden mutation.
- **Split drawing code by mark shape, not by chart type** — 17 chart types, 6 mark shapes.
- **Atomic grain**: one fact-table row = one event. Aggregation happens only in the 02 projection, and three chart shapes there do not aggregate at all.

## Don'ts

- Don't name a chart type in the 01 prompt — scenarios come from the domain, not from visualization templates. Intents stop at the view class.
- Don't aggregate at generation time.
- Don't let the LLM judge feasibility; don't reintroduce an LLM call after 01.
- Don't split the scenario back out into its own LLM call or its own stage interface.
- Don't re-render a figure to fix it. If a value can't be read off the image, drop it from the value targets. (Rendering the same FigureSpec under a *different* style vector is a product, not a retry.)
- Don't add a second plotting backend before the style ablation demands it.
- Don't add a chart type whose four conditions duplicate an existing row — make it a style dimension.
- Don't write ground truth that wasn't recorded during drawing.
- Don't change a data interface without also updating its sample in `tests/samples/` and its `schema_version`.
- Don't describe changes relative to an earlier version of the spec — the spec states only what is current.

## Scope note on other outputs

The recorded metadata (scenario, fact table, schema, FigureSpec, three record layers, style vector) supports more than the eight training targets: QA pairs, chart code, style-paired samples, layout-paired samples, multi-figure consistency sets. These are extra export functions over the same records, not extra pipeline runs. QA generation is deliberately out of the current line of work, but the record must keep everything it would need — `key`, aggregated values, row counts, dependency graph.

## Maintenance

`storyline/parsebench_chart/` and the code must stay in sync. Update `IMPL_PLAN.md`'s checklist as work lands, `README.md` for setup or CLI changes, and `slides/parsebench_talk.html` when the method changes. Keep the hospital ER example consistent across all docs — the numbers in 01/02/03/04/05 are chained (900 rows → 80 candidates → 36 pass → 8 figures; 协和 42.3 / 华山 35.8 / 瑞金 28.1).
