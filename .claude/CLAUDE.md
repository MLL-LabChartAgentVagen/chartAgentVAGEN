# CLAUDE.md

## Project

Chart data generation for **grounded transcription**: synthesize charts where every rendered value carries the pixel box it was drawn in. Output unit is `(key, value, box)`. Ground truth is recorded while drawing — never obtained by annotating finished images.

- Spec: `storyline/parsebench_chart/` — the single source of truth.
- Plan: `IMPL_PLAN.md` — module layout, data interfaces, checklist.
- Running example used by every spec doc: hospital ER wait times (3 hospitals × 4 departments × 3 severity levels, 900 rows).

## Pipeline

Six stages, one forward data flow. LLM appears in 01–03 only.

| Stage | Package | In → Out | LLM |
|---|---|---|---|
| 01 scenario | `s01_scenario` | domain pool → ScenarioContext | yes |
| 02 facts | `s02_facts` | ScenarioContext → FactTable + TableSchema | yes, writes the generating script |
| 03 figure | `s03_figure` | table + schema + intent → FigureSpec | yes, picks index numbers |
| 04 render | `s04_render` | FigureSpec + StyleVector → image + L0/L1 | no |
| 05 record | `s05_record` | RenderOutput → Record (3 layers + `readable`) | no |
| 06 targets | `s06_targets` | Record → training target files | no |

Shared layer: `interfaces/` (the five data interfaces), `registry/` (chart types), `common/` (seeds, geometry, cache, llm, dedup).

## How the tricky parts work

- **Record while drawing.** Every mark writes its box, key, and values at the moment it is drawn, using the plotting library's own coordinate transform. Never draw first and parse the image afterwards.
- **Freeze layout.** Figure size, dpi, and the axes rectangle are fixed. Auto-layout moves the plot area after the fact and silently invalidates every recorded box.
- **Filter before select.** 03 enumerates, filters by rule, then lets the LLM pick from the filtered list. The LLM cannot produce an infeasible figure, so there is no validate-and-retry loop.
- **Feasibility is a lookup, not a judgement.** `additive` / `ordered` / `unit` are declared once in 02; 03 only matches them against the registry.
- **Readability is decided after rendering** from actual pixel geometry plus the encoding channel (length/position → maybe; angle/area/color → no). Unreadable marks drop out of value targets but stay in localization targets.
- **Three self-checks on the production path** (`s05_record/selfcheck.py`): is there anything inside the box, does the value read back from pixels match, does the answer stay the same under a different style. Failure discards the figure and logs the reason.
- **One coordinate convention**: pixels, origin top-left, `[x0, y0, x1, y1]`, image size recorded alongside.
- **Keys are ordered string tuples** — `("协和", "外科")`. All three record layers join on `(figure_id, panel_id, key)`.

## Code Standards

- **Simple, short, clear** — the minimal implementation that solves the problem. No premature abstraction, no oversized files.
- **One file, one responsibility.** Anything used by two stages lives in `common/` or `interfaces/`.
- **Extract a helper the second time a pattern repeats**, not the first, never the third.
- **Type hints everywhere**; avoid `Any`. `@dataclass` for every structured object, not loose dicts.
- **Stages talk only through `interfaces/`** — no stage imports another stage's internals.
- **Determinism**: `(input, seed) -> output` bit-for-bit. No global random state, no hidden mutation.
- **Split drawing code by mark shape, not by chart type** — 18 chart types, 6 mark shapes.
- **Atomic grain**: one fact-table row = one event. Aggregation happens only in the 03 projection.

## Don'ts

- Don't mention chart types in 01 — scenarios come from the domain, not from visualization templates.
- Don't aggregate at generation time.
- Don't let the LLM judge feasibility.
- Don't re-render. If a value can't be read off the image, drop it from the value targets.
- Don't add a second plotting backend before the style ablation demands it.
- Don't write ground truth that wasn't recorded during drawing.
- Don't generate QA pairs — this pipeline produces transcription and grounding targets, not questions.
- Don't change a data interface without also updating its sample in `tests/samples/` and its `schema_version`.

## Maintenance

`storyline/parsebench_chart/` and the code must stay in sync. Update `IMPL_PLAN.md`'s checklist as work lands, and `README.md` for setup or CLI changes. Keep the hospital ER example consistent across all docs — the numbers in 03/04/05/06 are chained.
