# CLAUDE.md

## Project

ChartAgent — atomic-grain chart understanding benchmark. **Code-as-DGP**: the LLM writes Python SDK scripts to synthesize a Master Fact Table; deterministic SQL projection (**Table Amortization**) yields 10–30+ multi-chart QA tasks per table with cross-chart arithmetic consistency.

## Architecture

Four-phase pipeline. LLM appears only in Phases 0–2; Phase 3 is fully deterministic.

- **Phase 0 — Domain Pool** (cached): 200+ fine-grained sub-topics, embedding-deduped, complexity-balanced.
- **Phase 1 — Scenario Contextualization**: sample one domain → realistic `scenario_context` (entities, metrics, target_rows). **No chart-type binding here.**
- **Phase 2 — Agentic Data Simulator**: LLM writes a `FactTableSimulator` script → `(Master DataFrame, Schema Metadata)`. Execution-error feedback + three-layer validator with auto-fix.
- **Phase 3 — View Extraction & QA**: SQL projection enumerates `(chart_type, column_binding)` views; operator-algebra pipelines build single- and multi-chart questions.

Schema Metadata is the Phase 2 ↔ Phase 3 contract.

## Code Standards

- **Simple, short, clear, concise** — prefer the minimal implementation that solves the problem; avoid over-engineering, premature abstraction, and overly large files.
- **Modular over monolithic** — split by responsibility; one file = one purpose. Anything reused across phases (sampling, validation, SQL projection, embedding utils) lives in a shared module, not duplicated per phase.
- **Reusable building blocks** — extract a helper the second time a pattern repeats, not the first; never the third.
- **No redundancy** — no copy-pasted logic, no parallel implementations of the same idea, no dead code.
- **Type hints on every signature**; avoid `Any` unless truly unavoidable. Use `@dataclass` for any structured input/output (`ViewSpec`, `ScenarioContext`, `Check`, ...), not loose dicts.
- **Determinism** — `(declarations, seed)` → bit-for-bit reproducible. No hidden global state.
- **Atomic grain** — every Master Table row is one indivisible event; aggregation belongs to Phase 3.
- **Closed-form measures** — declare each measure once; never patch via successive overrides.
- **No LLM in Phase 3.**

## Key Patterns

- **`FactTableSimulator` SDK — two ordered steps**: Step 1 declare columns (`add_category`, `add_temporal`, `add_measure`, `add_measure_structural`); Step 2 declare relationships/patterns (`declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`).
- **Dimension groups** — within-group hierarchy via `parent`; cross-group via orthogonality or root-only DAG dependencies.
- **Measure DAG** — stochastic = root, structural = derived from formula; topological generation; cycles raise typed SDK exceptions fed back to the LLM (≤3 retries).
- **Operator algebra (Phase 3)** — every question is a typed pipeline `V → … → S` over Set / Scalar / Combinator / Bridge ops. **Operator–chart compatibility is the single filter** for view feasibility, multi-chart pairing, and pipeline sampling.
- **Difficulty = #ops** (1–2 Easy · 3–4 Medium · 5–6 Hard · 7+ Very Hard).

## Chart Type Registry

6 families · 16 types: Comparison (bar, grouped_bar) · Trend (line, area) · Distribution (histogram, box, violin) · Composition (pie, donut, stacked_bar, treemap) · Relationship (scatter, bubble, heatmap, radar) · Flow (waterfall, funnel).

## Don'ts

- Don't bind chart types in Phase 1 — scenarios are domain-driven.
- Don't aggregate at generation time.
- Don't patch a measure across multiple SDK calls.
- Don't put cross-group dependencies on non-root columns; don't allow cycles in any DAG.
- Don't call the LLM in Phase 3.
- Don't add scoring heuristics or QA templates — compatibility is the only filter.

## Maintenance

Keep `storyline/` (the spec) and the implementation in sync. Update `README.md` for setup/CLI/SDK-surface changes.
