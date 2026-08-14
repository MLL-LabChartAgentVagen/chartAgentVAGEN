# CLAUDE.md

## Project

**Grounded transcription** chart data generation. Programmatically synthesize charts where every rendered value carries the pixel region it was drawn in. Output unit is `(key, value, region)`. Ground truth comes from instrumenting the renderer — never from annotating images.

Spec lives in `storyline/parsebench_chart/`. Implementation plan in `IMPL_PLAN.md`.

## Architecture

Four execution stages plus two contracts. LLM appears in stages 01–03 only; stage 04 is fully deterministic.

- **01 Scenario** — domain pool (cached) → scenario context + analytical intent. LLM.
- **02 Fact table** — LLM writes a DGP script against a 4-method SDK; deterministic engine executes it → atomic row-level table + Schema Metadata.
- **03 Figure** — enumerate views (deterministic) → filter (deterministic) → LLM picks from the filtered candidate list → FigureSpec. **Filter before select**, never the reverse.
- **04 Render** — FigureSpec + independently sampled style vector → page image + L0/L1 geometry. Single instrumented backend.
- **05 Provenance** (contract) — three-layer record format, recoverability rule, three verification gates.
- **06 Output** (contract) — provenance record → training targets, as a pure function.

Schema Metadata is the 02 ↔ 03 contract. The provenance record is the 04 ↔ 06 contract.

## Code Standards

- **Simple, short, clear, concise** — prefer the minimal implementation that solves the problem; avoid over-engineering, premature abstraction, and overly large files.
- **Modular over monolithic** — split by responsibility; one file = one purpose. Anything reused across stages (sampling, embedding dedup, geometry transforms, caching) lives in a shared module.
- **Reusable building blocks** — extract a helper the second time a pattern repeats, not the first; never the third.
- **No redundancy** — no copy-pasted logic, no parallel implementations of the same idea, no dead code.
- **Type hints on every signature**; avoid `Any`. Use `@dataclass` for any structured input/output (`ViewSpec`, `FigureSpec`, `Mark`, `StyleVector`, ...), not loose dicts.
- **Determinism** — `(declarations, seed)` → bit-for-bit reproducible. No hidden global state.
- **Stages are pure functions** — `f(input, seed) -> output`, cached by content hash. No stage reaches backwards.
- **Atomic grain** — every fact-table row is one indivisible event; aggregation happens only in the SQL projection.

## Key Patterns

- **SDK — four methods**: `dim`, `time`, `measure`, `emit`. Dependencies inferred from expression free variables, not declared. `unit` / `additive` / `ordered` are declared once in 02 and only looked up downstream.
- **Registry is the single source of chart-type truth** — structure (for enumeration), semantics (for filtering), visual (mark shape + encoding channel, for instrumentation and recoverability). Tiered delivery: Tier 1 first, end to end.
- **Provenance emission is distributed** — projector emits L2 row counts, instrumented renderer emits L1 marks, page compositor emits L0 element boxes. Merging is a pure join.
- **Recoverability is computed after rendering** from actual pixel geometry plus the encoding channel. Unrecoverable marks drop out of value targets but stay in localization targets.
- **One coordinate convention** — pixels, origin top-left, `[x0, y0, x1, y1]`, image width/height recorded alongside.
- **Every image degradation has an analytic geometric transform**; boxes are mapped through it.

## Don'ts

- Don't bind chart types in 01 — scenarios are domain-driven.
- Don't aggregate at generation time.
- Don't let the LLM judge feasibility — feasibility is table lookup over declarations made in 02.
- Don't re-render. If a value is unrecoverable, drop it from the value target set.
- Don't add a second rendering backend before the style ablation demands it.
- Don't write ground truth that was not produced by instrumentation.
- Don't generate QA pairs — this pipeline produces transcription and grounding targets, not questions.

## Maintenance

`storyline/parsebench_chart/` is the spec and must stay in sync with the implementation. Update `IMPL_PLAN.md`'s checklist as work lands, and `README.md` for setup/CLI changes.
