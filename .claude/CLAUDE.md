# CLAUDE.md

## Project

Chart data generation for **grounded transcription**: synthesize charts where every rendered value carries the pixel box it was drawn in. Output unit is `(key, value, box)`. Ground truth is recorded while drawing — never obtained by annotating finished images.

- Spec: `storyline/parsebench_chart/` — the single source of truth.
- **All code is English** — comments, docstrings, exception text, prompts, CLI output. So is all pipeline-produced content: column values, units, scenario prose, intent sentences, captions, axis labels, slides. Chinese stays in the documents: `storyline/`, `README.md`, `IMPL_PLAN.md`.
- **Docstrings stand on their own.** Never refer to a stage by its number alone or to a spec section by number (`03 → 04`, `§4`, `L1`); say what the thing does and name the component. A spec path may follow as a pointer, never as the explanation. The running example is a US emergency department.
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

Shared layer: `interfaces/` (six data interfaces), `registry/` (`charts.py` condition table, `conditions.py` predicate, `channels.py` readability), `common/` (seeds, geometry, pixel readback, cache), `report.py` (the readable view of an artifact: Mermaid diagrams and a terminal summary, written automatically beside every schema — a new stage adds a section here rather than a script under `tools/`).

`src/llmkit/` is a separate package that knows nothing about chartgen: model calls, JSON-mode with feedback retry, on-disk response cache, embedding dedup, concurrent batch. 01 uses it; so will any future multi-model evaluation. Adding a provider is one file.

## How the tricky parts work

- **One LLM call, three outputs.** Scenario prose, the declaration script, and the intents — each intent carrying its target columns, aggregate, and view class — all come out of the same call. The script *is* the formalized scenario, so splitting this into two calls would insert a lossy JSON layer (hierarchy, orderedness, units and additivity are not explicit in prose) with no feedback path back upstream. Because the columns and the intents are written together, intent binding holds by construction rather than by inference.
- **Feasibility is decided at declaration time.** Structural and semantic conditions depend only on column declarations (`dim` value lists give cardinality; `time` start/end/freq give point counts; `additive` and `ordered` — `None` / `"ordinal"` / `"stage"` — are declared fields). 01 asks only whether each family is non-empty; it never expands the combinations. Only variance / distinctness / actual cell counts need real data.
- **02 has no LLM, and there is no candidate list.** Three kinds of figure, three mechanisms, and only one needs a random number:
  - **意图图 / intent figure — constructed.** The binding fixes columns, aggregate and family; the condition table fixes the type; a deterministic order breaks ties. Its value is caption: only an intent figure's caption carries information not readable off the image.
  - **多面板图 / multi-panel — derived.** The anchor must be a figure already accepted standalone (so the shared view yields a free paired sample), and the partner panel is computed by the relationship rule.
  - **轮转图 / rotation — sampled with rejection.** Per family, draw (type, columns, aggregate), validate, project, admit or redraw, up to T tries.
  Never reintroduce enumeration here. Enumerating every legal view means hundreds to thousands of candidates, each needing a full projection pass, to ship about a dozen figures.
- **Diversity is an admission test, not a count.** Reject a candidate when the batch already holds a figure with the **same key set and the same mark shape** — no threshold to tune. That pair is the right one because the output unit is `(key, value, box)`. `K_max` is only a render/storage budget; a count admits eight variations of `bar(hospital × …)`. Multi-panel figures are exempt: their value is the layout form, and repeated keys are what makes them a paired sample.
- **Row filters live only in `panel.py`.** They serve exactly one relationship (time comparison) and are sliced off the anchor on demand, never a sampling dimension of ViewSpec.
- **Projection is always one SELECT, in four shapes.** Grouped scalar (bar family, line, area, pie, heatmap, compound, waterfall, funnel), grouped five-number (box), binned count (histogram), and **per-row with no grouping** (scatter). Scatter needs deterministic down-sampling to the type's point cap, and its L2 degenerates: `rows` is 1 per mark, and histogram's `rows` equals its `count`. The aggregate set follows the shape — `FIVE_NUM`, `BIN_COUNT`, `NONE` are not SUM/AVG/COUNT. The four are a branch point because value dict size, applicable data filters and L2 usefulness all differ.
- **The names describe how a figure was chosen**, not its importance. Never reintroduce "main / supplementary" — that reading is what confuses readers.
- **Multi-panel figures are composed by rule** in `s02_figure/panel.py`, from five relationships: orthogonal slice (2–4 panels, the small-multiples workhorse), drill-down (2–3), time comparison (2 or 4), dual metric (2, compound), part-whole (2). The relationship determines panel count, layout and what is shared. Not optional decoration: `applies_to_panels` is trivial on single-panel figures, so without this the target is always empty. **A shared legend requires every panel to use the same series column** — that is a FigureSpec constraint the style vector cannot override. Same-type across panels vs. mixed-type (bar + line) is a style dimension; both are wanted.
- **Record while drawing.** Every mark writes its box, key, and values at the moment it is drawn, using the plotting library's own coordinate transform. Never draw first and parse the image afterwards.
- **Freeze layout.** Figure size, dpi, and the axes rectangle are fixed. Auto-layout moves the plot area afterwards and silently invalidates every recorded box.
- **Readability is decided after rendering** from actual pixel geometry plus the encoding channel (length/position → maybe; angle/area/color → no). The rule is defined once, in `chart_types.md` §4. Unreadable marks drop out of value targets but stay in localization targets.
- **Three self-checks on the production path** (`s04_record/selfcheck.py`): is there anything inside the box, does the value read back from pixels match, does the answer stay the same under a different style. Failure discards the figure and logs the reason. The third one needs no extra render — it consumes the style-paired versions that are a product in their own right.
- **The first two self-checks are also the RL reward.** They need only the image and the claimed `(value, box)`, not ground truth. `common/readback.py` holds the one implementation; `s04_record/selfcheck.py` feeds it the renderer's record, `s05_output/verify.py` feeds it the model's output.
- **Visual variants live in the style vector, not the type table.** Two "types" whose four condition columns, mark shape and value dict are identical (solid pie vs. donut) occupy one row in `registry/charts.py`; the difference is a `StyleVector` field.
- **One coordinate convention**: pixels, origin top-left, `[x0, y0, x1, y1]`, image size recorded alongside.
- **Keys are ordered string tuples** — `("Mercy General", "Surgery")`. All three record layers join on `(figure_id, panel_id, key)`.

## Code Standards

- **Simple, short, clear** — the minimal implementation that solves the problem. No premature abstraction, no oversized files.
- **One file, one responsibility.** Anything used by two stages lives in `common/`, `registry/`, or `interfaces/`.
- **Extract a helper the second time a pattern repeats**, not the first, never the third.
- **Type hints everywhere**; avoid `Any`. `@dataclass` for every structured object, not loose dicts.
- **Stages talk only through `interfaces/`** — no stage imports another stage's internals.
- **Determinism**: `(input, seed) -> output` bit-for-bit. No global random state, no hidden mutation.
- **Split drawing code by mark shape, not by chart type** — 13 chart types, 5 mark shapes.
- **Atomic grain**: one fact-table row = one event. Aggregation happens only in the 02 projection, and three chart shapes there do not aggregate at all.

## Don'ts

- Don't name a chart type in the 01 prompt — scenarios come from the domain, not from visualization templates. Intents stop at the view class.
- Don't aggregate at generation time.
- Don't let the LLM judge feasibility; don't reintroduce an LLM call after 01; don't reintroduce enumeration into 02.
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

`storyline/parsebench_chart/` and the code must stay in sync. Update `IMPL_PLAN.md`'s checklist as work lands, `README.md` for setup or CLI changes, and `slides/parsebench_talk.html` when the method changes. Keep the hospital ER example consistent across all docs — the numbers in 01/02/03/04/05 are chained (900 rows → 8 figures = 3 intent + 2 multi-panel + 3 rotation; Mercy General 42.3 / St. Luke's 35.8 / Riverside 28.1; box [168,196,278,520]).
