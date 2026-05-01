# Atomic-Grain Programmatic Data Synthesis for Chart Understanding Benchmarks

> **Paradigm:** From **LLM-as-Data-Generator** to **LLM-as-Data-Programmer**. The LLM writes executable Python scripts calling a type-safe SDK to construct **Atomic-Grain Generative Fact Tables** — row-level event records with full dimensional hierarchy, inter-column correlations, and injected statistical patterns. Deterministic SQL projection (**Table Amortization**) then extracts coherent multi-chart QA tasks from a single Master Table, guaranteeing cross-chart arithmetic consistency by construction.

---

## 1. Design Philosophy

Three interlocking principles address the structural deficits of existing chart QA datasets (ChartQA, PlotQA, ChartBench): shallow data depth, arithmetic hallucinations from LLM-generated numbers, and zero cross-chart consistency.

| Principle | Status Quo | Ours |
|-----------|-----------|------|
| **Generative Fact Tables** | 5-row aggregated data — no provenance, no drill-down. | **Atomic event records** (each row = one transaction/visit/reading) preserving full dimensional hierarchy and long-tail statistics. |
| **Agentic Data Simulator (SDK)** | LLM writes fragile JSON configs or raw numbers. | **LLM writes Python scripts** calling a type-safe SDK. Native **Execution-Error Feedback Loop** catches mathematical impossibilities and enables self-correction. |
| **Table Amortization** | One table per chart; pie and line chart from the same domain may have inconsistent totals. | **One Master Table → 10–30+ tasks.** Deterministic SQL projections guarantee every derived chart view shares the same ground-truth arithmetic. |

---

## 2. Chart Type Registry

The meta-configuration layer defining 6 families and 16 chart types. Each type specifies structural requirements, supported data patterns, and QA capabilities.

> See [Chart Type Registry](chart_type_registry.md)

---

## 3. The 4-Phase Pipeline (Phase 0–3)

```
 ┌──────────────────────────────────────────────────────────────┐
 │  PHASE 0: Domain Pool Construction (one-time, cached)        │
 │  LLM batch-generates 200+ fine-grained vertical domains      │
 │  across 15+ super-sectors with structured metadata.          │
 │  Embedding dedup + complexity balancing → typed JSON pool.   │
 └────────────────────────┬─────────────────────────────────────┘
                          ▼
              [ Domain Pool (200+ domains, cached artifact) ]
                          ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  PHASE 1: Scenario Contextualization                         │
 │  Sample Domain → LLM instantiates realistic Data Context     │
 │  (entities, metrics, temporal grain, target volume)           │
 └────────────────────────┬─────────────────────────────────────┘
                          ▼
 ┌──────────────────────────────────────────────────────────────┐  ◀──┐
 │  PHASE 2: Agentic Data Simulator (SDK-Driven)                │     │ Execution
 │  LLM writes Python SDK script defining:                      │     │ Error
 │    Schema (with orthogonal pairs) + Distributions +           │     │ Feedback
 │    Correlations + Patterns + Realism                         │     │
 │  Engine executes → Master Table + Schema Metadata            │  ───┘
 │  Three-layer validation; auto-fix without LLM re-call        │
 └────────────────────────┬─────────────────────────────────────┘
                          ▼
              [ Master Fact Table + Schema Metadata ]
                          ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  PHASE 3: View Amortization & QA Instantiation               │
 │  Deterministic SQL projection → single & multi-chart views   │
 │  Rule-based single & cross-chart QA generation               │
 │  Pattern-triggered hard questions                            │
 └──────────────────────────────────────────────────────────────┘

Output: {Chart Images, Questions, Answers, Reasoning Chains} × N
```

> **LLM usage:** The LLM is called in Phase 0 (domain pool, one-time batch), Phase 1 (scenario instantiation), and Phase 2 (SDK script). Phase 3 is entirely deterministic — no LLM calls, no randomness beyond the fixed seed.

---

## 4. Phase Navigation

- **[Phase 0: Domain Pool Construction](phase_0.md)** — One-time batch generation of 200+ fine-grained domains across 15+ super-sectors. Embedding-based deduplication, complexity-tier balancing, and a typed JSON schema produce a cacheable artifact that seeds all downstream generation.
- **[Phase 1: Scenario Contextualization](phase_1.md)** — Samples a domain from the Phase 0 pool and instantiates a concrete, realistic scenario. No chart types mentioned; data is born from business context, not visualization templates.
- **[Phase 2: Agentic Data Simulator](phase_2.md)** — **Core technical contribution.** LLM writes SDK scripts that unify Schema definition and DGP in a single executable pass. Includes orthogonal pair declarations, execution-error feedback, and three-layer validation.
- **[Phase 3: View Amortization & QA](phase_3.md)** — Deterministic engine extracts diverse chart views from one Master Table via SQL operators, composes multi-plot dashboards, and generates multi-tier QA pairs with reasoning chains.
- **[Chart Type Registry](chart_type_registry.md)** — Meta-configuration: 6 families, 16 chart types, with structural requirements and QA capabilities.

---

## 5. Table Amortization: One Table, Many Tasks

Core value: **1 LLM call → 1 Python script → 1 Master Table → 10–30+ logically coherent tasks**

```python
def generate_tasks(master_table, schema_metadata, config):
    tasks = []

    # Step 1: Enumerate all feasible single-chart views
    feasible_views = ViewEnumerator().enumerate(schema_metadata, master_table)

    # Step 2: Single-plot tasks
    for view_spec in feasible_views[:config.max_single_views]:
        view = extract_view(master_table, view_spec)
        chart = render_chart(view, view_spec)
        qa = generate_intra_qa(view, view_spec)
        qa += PatternDetector().detect_and_generate_qa(view, view_spec, schema_metadata["patterns"])
        tasks.append(Task(charts=[chart], qa=qa))

    # Step 3: Multi-plot dashboard tasks (k=2,3,4)
    composer = DashboardComposer()
    for target_k in [2, 3, 4]:
        dashboards = composer.compose(feasible_views, schema_metadata, target_k)
        for dashboard in dashboards[:config.max_dashboards_per_k]:
            views = [extract_view(master_table, vs) for vs in dashboard.view_specs]
            charts = [render_chart(v, vs) for v, vs in zip(views, dashboard.view_specs)]
            qa = generate_inter_qa(views, dashboard)
            tasks.append(Task(charts=charts, qa=qa))

    return tasks
```

---

## 6. Comparison with Prior Work

| Dimension | ChartQA (CVPR'22) | PlotQA (WACV'20) | ChartBench (ACL'24) | **Ours** |
|-----------|-------------------|-------------------|---------------------|----------|
| Data source | Web-crawled images | Template synthesis | Hybrid | **LLM-authored simulator programs** |
| Data depth | Surface aggregates | Aggregates | Aggregates | **Atomic-grain fact tables** |
| Distribution control | None | Uniform/Normal | Semi-fixed | **SDK-controlled: mixtures, copulas, conditional** |
| Cross-chart consistency | None | None | None | **Guaranteed (shared Master Table)** |
| Error correction | Manual / discard | None | Heuristic rules | **Code Execution Feedback Loop** |
| Multi-chart reasoning | None | None | Limited | **Dashboard-level cross-chart QA** |
| Reproducibility | ✗ | ✓ | Partial | **✓ (SDK + seed)** |

---

## 7. Core Contributions

1. **Atomic-Grain Data Synthesis.** Every row is an indivisible event record. All chart views are derived downstream via SQL projection — never fabricated by the LLM. This breaks the coupling between data granularity and chart type that plagues existing benchmarks.

2. **Agentic Data Simulator (Code-as-DGP).** The LLM writes executable Python calling a type-safe SDK. Schema definition and data generation program are unified in a single code pass. Execution-Error Feedback replaces fragile JSON validation, catching semantic impossibilities (infeasible correlations, degenerate distributions) at the mathematical level.

3. **Orthogonal Pair Declarations.** Pairwise independence between categorical dimensions is explicitly declared and validated, enabling cross-cutting multi-chart dashboards and orthogonal reasoning QA that prior benchmarks cannot generate.

4. **Table Amortization.** One Master Table serves 10–30+ tasks (multi-chart × multi-QA), maximizing the value of each LLM call while guaranteeing cross-chart arithmetic consistency by construction.
