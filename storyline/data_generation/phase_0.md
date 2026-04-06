## PHASE 0: Domain Pool Construction

> **Purpose:** Build a cached pool of 200+ fine-grained domains that seeds all downstream data generation. Runs once; all subsequent phases sample from its output.

---

### 0.1 Domain Taxonomy

Domains are organized into two levels: **Topic → Sub-topic**. Topics provide broad industry coverage; sub-topics are specific enough to produce realistic data scenarios.

**Seed Topics (5 examples — extend as needed):**

| # | Topic | Example Sub-topics |
|---|-------|--------------------|
| 1 | Healthcare | ICU bed turnover analytics, clinical trial enrollment tracking |
| 2 | Finance | Credit card fraud detection logs, mutual fund flow analytics |
| 3 | Retail & E-Commerce | Flash sale conversion funnels, customer return behavior |
| 4 | Transportation & Logistics | Urban rail transit scheduling, last-mile delivery performance |
| 5 | Energy & Utilities | Wind farm sensor monitoring, residential electricity demand |

> Generate additional topics using the **Topic Generation Prompt** below.

---

### 0.2 Topic Generation Prompt

**System prompt:**
```text
You are a domain expert building a diverse topic pool for a chart understanding
benchmark. Rules:
1. Each topic is a broad, industry-level category.
2. Topics must be mutually non-overlapping in scope.
3. Aim for full coverage across different industries and fields.
4. Return a JSON array of strings.
```

**User prompt:**
```text
Generate {n} new topics. Existing topics (avoid overlap): {existing_topics}

=== ONE-SHOT EXAMPLE ===
Existing topics: ["Healthcare", "Finance"]
Generate 3 new topics.
Output: ["Manufacturing", "Education", "Agriculture"]
```

---

### 0.3 Sub-topic Generation Prompt

**System prompt:**
```text
You are a data domain expert building fine-grained sub-topics for a chart
understanding benchmark. Rules:
1. Each sub-topic is a concrete analytical context (not a broad label).
2. Sub-topics must be mutually non-overlapping and collectively cover the topic.
3. Balance complexity tiers roughly equally:
   - simple: Single entity type, 1-2 metrics, straightforward time series.
   - medium: Multiple correlated metrics, 2+ entity types.
   - complex: Nested hierarchies, 3+ interdependent metrics.
4. For each sub-topic, provide:
   - "name": Concise description (5-10 words)
   - "topic": Parent topic
   - "complexity_tier": "simple" | "medium" | "complex"
   - "typical_entities_hint": 2-3 entity types
   - "typical_metrics_hint": 2-3 measures with units
   - "temporal_granularity_hint": "hourly"|"daily"|"weekly"|"monthly"|"quarterly"|"yearly"
5. Return a JSON array.
```

**User prompt:**
```text
Topic: {topic}
Generate {n} new sub-topics. Existing sub-topics (avoid overlap): {existing_subtopics}

=== ONE-SHOT EXAMPLE ===
Topic: "Transportation & Logistics"
Existing sub-topics: ["Urban rail transit scheduling"]
Generate 2 new sub-topics.
Output:
[
  {
    "name": "Last-mile delivery performance tracking",
    "topic": "Transportation & Logistics",
    "complexity_tier": "medium",
    "typical_entities_hint": ["delivery zones", "courier teams"],
    "typical_metrics_hint": [
      {"name": "delivery_time", "unit": "minutes"},
      {"name": "success_rate", "unit": "%"}
    ],
    "temporal_granularity_hint": "daily"
  },
  {
    "name": "Airport runway utilization and delay propagation",
    "topic": "Transportation & Logistics",
    "complexity_tier": "complex",
    "typical_entities_hint": ["runways", "airlines", "time slots"],
    "typical_metrics_hint": [
      {"name": "turnaround_time", "unit": "minutes"},
      {"name": "delay_minutes", "unit": "minutes"}
    ],
    "temporal_granularity_hint": "hourly"
  }
]
```

---

### 0.4 Quality Check — Overlap Detection

After generation, check for semantic overlap within the generated list using embedding similarity. This single checker is shared by both topic-level and sub-topic-level pools.

```python
def check_overlap(items: list[str],
                   model: str = "text-embedding-3-small",
                   threshold: float = 0.80) -> list[tuple[str, str, float]]:
    """Return pairs whose cosine similarity >= threshold.

    Works for both topics and sub-topics — just pass the name list.
    """
    embeddings = get_embeddings(items, model=model)   # items -> vectors
    sim_matrix = cosine_similarity(embeddings)
    overlaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if sim_matrix[i][j] >= threshold:
                overlaps.append((items[i], items[j], sim_matrix[i][j]))
    return overlaps  # empty list = no overlap, good to go
```

**Usage:**
```python
# Check topics
overlaps = check_overlap(["Healthcare", "Medicine & Health", "Finance"])
# -> [("Healthcare", "Medicine & Health", 0.91)]  — flag for removal / merge

# Check sub-topics under a single topic
subtopic_names = [d["name"] for d in generated_subtopics]
overlaps = check_overlap(subtopic_names)
```

If overlaps are found, remove or regenerate the flagged items before proceeding.

---

### 0.5 Output Schema

```json
{
  "version": "1.0",
  "generated_at": "2024-12-15T10:30:00Z",
  "total_domains": 213,
  "diversity_score": 0.82,
  "complexity_distribution": {"simple": 71, "medium": 72, "complex": 70},
  "topic_coverage": {"Healthcare": 15, "Finance": 14, "...": "..."},
  "domains": [
    {
      "id": "dom_001",
      "name": "ICU bed turnover analytics",
      "topic": "Healthcare",
      "complexity_tier": "complex",
      "typical_entities_hint": ["hospitals", "ICU wards", "patient categories"],
      "typical_metrics_hint": [
        {"name": "occupancy_rate", "unit": "%"},
        {"name": "length_of_stay", "unit": "days"}
      ],
      "temporal_granularity_hint": "daily"
    }
  ]
}
```

---

### 0.6 Sampling Interface for Phase 1

```python
class DomainSampler:
    """Stratified sampler drawing from the Phase 0 domain pool."""

    def __init__(self, pool_path: str):
        with open(pool_path) as f:
            self.pool = json.load(f)["domains"]
        self.used_ids = set()

    def sample(self, n: int = 1, complexity: str = None) -> list[dict]:
        """Sample n domains without replacement. Resets at 80% exhaustion."""
        candidates = [d for d in self.pool if d["id"] not in self.used_ids]
        if complexity:
            candidates = [d for d in candidates if d["complexity_tier"] == complexity]
        if len(candidates) < n:
            self.used_ids.clear()
            candidates = self.pool if not complexity else \
                [d for d in self.pool if d["complexity_tier"] == complexity]
        selected = random.sample(candidates, min(n, len(candidates)))
        self.used_ids.update(d["id"] for d in selected)
        return selected
```
