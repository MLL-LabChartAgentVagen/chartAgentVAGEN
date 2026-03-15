## PHASE 1: Scenario Contextualization

This phase bridges the real world and the simulation engine. It generates no data — it produces **semantic anchors** that constrain Phase 2's data generation to be realistic, diverse, and domain-grounded.

> **Input:** Domain Pool artifact from [Phase 0](phase_0.md) (200+ typed domains with metadata).
> **Output:** A concrete Scenario Context (JSON) ready for Phase 2's SDK script generation.

---

### 1.1 Domain Sampling

Phase 1 draws from the Phase 0 domain pool using **stratified without-replacement sampling** to maintain complexity balance across the benchmark. The `DomainSampler` (defined in Phase 0 §0.6) handles tier-aware selection, ensuring each benchmark epoch draws evenly from simple, medium, and complex domains.

```python
# Per-generation: sample one domain from the Phase 0 pool
sampler = DomainSampler("domain_pool.json")
domain = sampler.sample(n=1)[0]
# domain contains: name, topic, complexity_tier, entity/metric/temporal hints
```

The sampled domain's full metadata — `typical_entities_hint`, `typical_metrics_hint`, and `temporal_granularity_hint` — is passed directly to the scenario instantiation prompt as structured context, allowing the LLM to ground its output in domain-specific knowledge.

---

### 1.2 Scenario Instantiation Prompt

**System prompt:**
```text
You are an expert Data Simulator Architect designing realistic data scenarios
for a multimodal chart understanding benchmark.

Rules:
1. "scenario_title": A specific, realistic title including time period, organization,
   and analytical focus (e.g., "2024 H1 Shanghai Metro Ridership Log").
2. "data_context": Describe WHO collected this data, WHY, and WHEN. Use a realistic
   business or scientific tone. Reference real-world organizations, agencies, or
   institutions where appropriate.
3. "key_entities": Provide 3-8 specific, named categorical entities. Use real-world
   names (e.g., actual hospital names, real city names, real product brands) — never
   generic placeholders like "Group A" or "Entity 1".
4. "key_metrics": Provide 2-5 quantifiable measures. Each must include a scientifically
   correct unit and a realistic value range grounded in domain knowledge.
5. "temporal_granularity": The data collection frequency (hourly | daily | weekly |
   monthly | quarterly | yearly).
6. "target_rows": Row count for the fact table, derived from complexity tier:
   simple → 200-500, medium → 500-1000, complex → 1000-3000.
   Adjust within range based on temporal span and entity count.
7. Ground all numbers, entities, and time windows in plausible real-world conditions.
   The scenario must read as if it were a real dataset from a real organization.
8. Output strictly valid JSON with no additional commentary.
```

**User prompt:**
```text
Generate a concrete, realistic data scenario for the following domain.

Domain metadata:
{domain_json}

Use the hints (typical_entities_hint, typical_metrics_hint, temporal_granularity_hint)
as soft guidance — you may adapt or override them when the specific scenario demands
different specifics, but stay faithful to the domain's scope and complexity tier.

=== ONE-SHOT EXAMPLE ===
Domain metadata:
{
  "name": "Urban rail transit scheduling",
  "topic": "Transportation & Logistics",
  "complexity_tier": "complex",
  "typical_entities_hint": ["metro lines", "stations", "time slots"],
  "typical_metrics_hint": [
    {"name": "ridership", "unit": "10k passengers"},
    {"name": "on_time_rate", "unit": "%"}
  ],
  "temporal_granularity_hint": "daily"
}

Output:
{
  "scenario_title": "2024 H1 Shanghai Metro Ridership & Operations Log",
  "data_context": "Shanghai Transport Commission collected daily ridership and
   operational performance data across core metro lines over January–June 2024
   to optimize peak-hour scheduling and identify maintenance bottlenecks.",
  "temporal_granularity": "daily",
  "key_entities": ["Line 1 (Xinzhuang–Fujin Rd)", "Line 2 (Pudong Intl Airport–East Xujing)",
                    "Line 8 (Shiguang Rd–Shendu Hwy)", "Line 9 (Songjiang South–Caolu)",
                    "Line 10 (Hongqiao Airport–New Jiangwan City)"],
  "key_metrics": [
    {"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]},
    {"name": "on_time_rate", "unit": "%", "range": [85.0, 99.9]},
    {"name": "equipment_failures", "unit": "count", "range": [0, 5]}
  ],
  "target_rows": 900
}

=== YOUR TASK ===
Output:
```

> **Why One-Shot?** Strict format control is critical for Phase 2's SDK to parse the scenario reliably. The one-shot example bounds LLM creativity, preventing exotic field types that downstream charts cannot render. This achieves the best fusion of realism and structural constraint (cf. Brown et al., 2020).

---

### 1.3 Scenario-Level Deduplication

Domain-level diversity (embedding deduplication, complexity balancing, topic coverage) is guaranteed by Phase 0's quality assurance pipeline. Phase 1 enforces **scenario-level** deduplication on top.

If multiple scenarios are generated from distinct but semantically adjacent domains (e.g., "hospital ER wait times" and "clinic triage delays"), their `data_context` fields may be nearly identical. We reuse Phase 0's `check_overlap` function (§0.4) to detect and reject such duplicates:

```python
from phase_0 import check_overlap  # reuse the shared embedding utility

def deduplicate_scenarios(scenarios: list[dict],
                          threshold: float = 0.85) -> list[dict]:
    """Remove near-duplicate scenarios based on data_context embedding similarity."""
    contexts = [s["data_context"] for s in scenarios]
    overlaps = check_overlap(contexts, threshold=threshold)

    # Collect indices to drop (keep the earlier-generated scenario)
    drop_indices = set()
    context_to_idx = {ctx: i for i, ctx in enumerate(contexts)}
    for ctx_a, ctx_b, sim in overlaps:
        drop_indices.add(context_to_idx[ctx_b])  # drop the later one

    return [s for i, s in enumerate(scenarios) if i not in drop_indices]
```

**Usage:**
```python
# After generating a batch of scenarios
scenarios = [generate_scenario(domain) for domain in sampled_domains]
scenarios = deduplicate_scenarios(scenarios, threshold=0.85)
# Near-duplicate scenarios (cosine similarity >= 0.85) are removed
```

> **Chart type isolation.** Phase 1 deliberately makes zero mention of chart types. Real data is born from business needs; charts are merely projections of data. Premature chart-type binding causes the LLM to generate template-hijacked schemas — this is the single most important design decision for breaking the "template disease" in existing benchmarks.
