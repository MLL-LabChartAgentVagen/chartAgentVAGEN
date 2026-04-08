---
title: "Atomic-Grain Programmatic Data Synthesis (AGPDS) — Framework Analysis"
date: "2026-02-25"
source_files:
  - storyline/chartagent_proposal.md
  - storyline/data_generation/data_generation_pipeline.md
  - storyline/data_generation/chart_type_registry.md
  - storyline/data_generation/phase_0.md
  - storyline/data_generation/phase_1.md
  - storyline/data_generation/phase_2.md
  - storyline/data_generation/phase_3.md
---

# AGPDS Framework Analysis

## 1. Core Design Principles

The following principles are extracted verbatim from the attached specification files.

### P1 — LLM-as-Data-Programmer (Code-as-DGP)

> "Paradigm shift: From **LLM-as-Data-Generator** to **LLM-as-Data-Programmer**. The LLM writes executable Python scripts calling a type-safe SDK — not fragile JSON configs or raw numbers."
> — `chartagent_proposal.md`, §2 (line 82)

The LLM's role is limited to authoring SDK scripts; all downstream computation is deterministic.

### P2 — Atomic-Grain Fact Tables

> "Every row is an indivisible event record. All chart views are derived downstream via SQL projection — never fabricated by the LLM."
> — `data_generation_pipeline.md`, §7 Core Contributions #1 (line 130)

Data is generated at the finest event-level granularity (e.g., one row = one hospital visit), breaking the coupling between data granularity and chart type.

### P3 — Table Amortization

> "1 LLM call → 1 Python script → 1 Master Table → **10–30+ logically coherent tasks**. All derived charts share the same ground-truth arithmetic by construction."
> — `chartagent_proposal.md`, §3 (line 180)

A single Master Table yields dozens of chart views via deterministic SQL projection, guaranteeing cross-chart arithmetic consistency.

### P4 — Dimension Groups & Orthogonality

> "Dimension groups are the central structural abstraction. Each categorical column belongs to exactly one named group. Columns within a group form a hierarchy via `parent`; columns across groups can be declared independent via `declare_orthogonal()`."
> — `phase_2.md`, §2.1.2 (line 43)

This abstraction eliminates O(n²) pairwise independence declarations and enables multi-view dashboard composition.

### P5 — Execution-Error Feedback Loop

> "Unlike JSON-config validation that catches only *syntactic* errors, code execution catches *semantic* impossibilities."
> — `chartagent_proposal.md`, §2.4 (line 154)

The SDK raises typed Python exceptions (e.g., infeasible correlation targets) and feeds them back to the LLM for self-correction (max 3 retries).

### P6 — Three-Layer Validation

> "After engine execution, a deterministic validator checks correctness at three levels."
> — `chartagent_proposal.md`, §2.5 (lines 166–174)

| Layer | What it checks | Example |
|-------|---------------|---------|
| L1: Structural | Row count, cardinality, orthogonal χ² | χ² p > 0.05 for orthogonal pairs |
| L2: Statistical | Correlation targets (±0.15), KS distribution tests, dependency residuals | target_r = −0.55 vs. actual −0.52 |
| L3: Pattern | Outlier z-scores, ranking reversals, trend breaks | Outlier z ≥ 2.0 |

Failures are auto-fixed by deterministic parameter adjustments without additional LLM calls.

### P7 — Chart-Type Isolation in Early Phases

> "Phase 1 deliberately makes zero mention of chart types. Real data is born from business needs; charts are merely projections of data. Premature chart-type binding causes the LLM to generate template-hijacked schemas — this is the single most important design decision for breaking the 'template disease' in existing benchmarks."
> — `phase_1.md`, §1.3, final blockquote (line 134)

### P8 — Rule-Based (No-LLM) Phase 3

> "LLM usage: Called only in Phases 0–2. Phase 3 is entirely deterministic — no LLM calls, no randomness beyond the fixed seed."
> — `data_generation_pipeline.md`, §3 (line 66)

---

## 2. Pipeline Architecture

The AGPDS pipeline is a strict 4-phase sequential workflow:

| Phase | Name | LLM? | Input | Output |
|-------|------|------|-------|--------|
| 0 | Domain Pool Construction | Yes (batch, one-time) | Seed topics | 200+ typed domains (JSON pool, cached) |
| 1 | Scenario Contextualization | Yes | Domain sample | Scenario Context JSON (entities, metrics, temporal grain) |
| 2 | Agentic Data Simulator | Yes (code-gen) | Scenario Context | Master Fact Table (DataFrame) + Schema Metadata |
| 3 | View Amortization & QA | **No** | Master Table + Metadata | Chart images, QA pairs, reasoning chains |

### Data Flow

```
Phase 0: Topics → Sub-topics → Domain Pool (cached JSON artifact)
                ↓
Phase 1: Domain sample → LLM → Scenario Context JSON
                ↓
Phase 2: Scenario → LLM writes SDK script (FactTableSimulator)
         → Sandbox executes → Master DataFrame + Schema Metadata
         → Three-Layer Validation (auto-fix loop)
                ↓
Phase 3: ViewEnumerator → feasible views (scored by Chart Selection Guide)
         → extract_view() → chart DataFrames
         → DashboardComposer → multi-chart dashboards (k=2,3,4)
         → Intra-view QA + Inter-view QA + Pattern-triggered QA
```

### Grain Granularity

The framework defines "atomic grain" as the finest indivisible event record — `chartagent_proposal.md` §7 Core Contribution #1:

> "every row = one transaction/visit/reading"

This contrasts with prior benchmarks that operate at aggregated (5–15 row) grain.  Distribution charts (histogram, box, violin) consume raw rows directly; aggregation charts (bar, pie, line) apply GROUP BY at view extraction time (`phase_3.md` §3.1.1, lines 14–22).

---

## 3. Theoretical Motivation

The AGPDS framework addresses three structural deficits of existing chart QA benchmarks, stated explicitly in `data_generation_pipeline.md` §1 (lines 7–15):

1. **Shallow data depth** — Prior datasets contain 5-row aggregated data with no provenance or drill-down capability. Atomic-grain tables preserve full dimensional hierarchy and long-tail statistics.

2. **Arithmetic hallucinations** — LLM-generated numbers lack consistency guarantees. By having the LLM write *programs* (not data), and executing them deterministically, all numbers are the output of controlled statistical engines.

3. **Zero cross-chart consistency** — Prior work creates one table per chart; a pie chart and line chart from the same domain may have inconsistent totals. Table Amortization guarantees every derived view shares the same ground-truth arithmetic.

The Operator Algebra (Part 1 of `chartagent_proposal.md`, lines 14–76) formalizes all chart QA as compositions of Set operators (Projection, Selection, Grouping, Sorting, Slicing) and Scalar operators (Aggregation, Positioning, Arithmetic), enabling systematic difficulty tiering.

---

## 4. Constraints & Anti-Patterns

### Explicitly Stated Constraints

| # | Constraint | Source |
|---|-----------|--------|
| C1 | Each row must be an indivisible event (ATOMIC_GRAIN) | `phase_2.md` §2.2, HARD CONSTRAINT #1 (line 114) |
| C2 | ≥ 2 dimension groups, each with ≥ 1 categorical column, plus ≥ 2 measures | `phase_2.md` §2.2, HARD CONSTRAINT #2 (line 115) |
| C3 | All column declarations (Step 1) BEFORE any relationship declarations (Step 2) | `phase_2.md` §2.2, HARD CONSTRAINT #3 (line 116) |
| C4 | ≥ 1 `declare_orthogonal()` between genuinely independent groups | `phase_2.md` §2.2, HARD CONSTRAINT #4 (line 117) |
| C5 | ≥ 1 `add_correlation()` and ≥ 2 `inject_pattern()` calls | `phase_2.md` §2.2, HARD CONSTRAINT #5 (line 118) |
| C6 | Output must be pure, valid Python returning `sim.generate()` | `phase_2.md` §2.2, HARD CONSTRAINT #6 (line 119) |
| C7 | Phase 3 must be entirely deterministic — no LLM calls | `data_generation_pipeline.md` §3 (line 66) |
| C8 | Chart type isolation: Phase 1 must make zero mention of chart types | `phase_1.md` §1.3 (line 134) |

### Prohibited Anti-Patterns

| Anti-Pattern | Rationale | Source |
|-------------|-----------|--------|
| LLM generating raw numbers | Causes arithmetic hallucinations; numbers should come from deterministic engine | `data_generation_pipeline.md` §1, Principle "Agentic Data Simulator" (line 14) |
| JSON-config for DGP | Catches only syntactic errors; cannot detect semantic impossibilities | `phase_2.md` §2.4 (line 303) |
| One table per chart | Destroys cross-chart consistency | `data_generation_pipeline.md` §1, Principle "Table Amortization" (line 15) |
| Premature chart-type binding | Induces "template disease" — LLM generates schemas hijacked by visualization templates | `phase_1.md` §1.3 (line 134) |
| Pairwise (O(n²)) independence declarations | Prevented by group-level orthogonality with automatic propagation | `phase_2.md` §2.1.2 (line 78) |
