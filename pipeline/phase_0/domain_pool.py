"""
AGPDS Phase 0: Domain Pool Construction

Builds a cached pool of fine-grained domains organized as Topic → Sub-topic.
Runs once; all subsequent phases sample from its output.

Components:
- DomainPool: LLM-driven domain taxonomy builder with caching
- DomainSampler: Stratified without-replacement sampler for Phase 1
- check_overlap: Embedding-based cosine similarity deduplication

Reference: phase_0.md
"""

import json
import random
import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ================================================================
# Prompts (§0.2 and §0.3)
# ================================================================

TOPIC_SYSTEM_PROMPT = """\
You are a domain expert building a diverse topic pool for a chart understanding
benchmark. Rules:
1. Each topic is a broad, industry-level category.
2. Topics must be mutually non-overlapping in scope.
3. Aim for full coverage across different industries and fields.
4. Return a JSON array of strings."""

TOPIC_USER_PROMPT_TEMPLATE = """\
Generate {n} new topics. Existing topics (avoid overlap): {existing_topics}

=== ONE-SHOT EXAMPLE ===
Existing topics: ["Healthcare", "Finance"]
Generate 3 new topics.
Output: ["Manufacturing", "Education", "Agriculture"]"""

SUBTOPIC_SYSTEM_PROMPT = """\
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
5. Return a JSON array."""

SUBTOPIC_USER_PROMPT_TEMPLATE = """\
Topic: {topic}
Generate {n} new sub-topics. Existing sub-topics (avoid overlap): {existing_subtopics}

=== ONE-SHOT EXAMPLE ===
Topic: "Transportation & Logistics"
Existing sub-topics: ["Urban rail transit scheduling"]
Generate 2 new sub-topics.
Output:
[
  {{
    "name": "Last-mile delivery performance tracking",
    "topic": "Transportation & Logistics",
    "complexity_tier": "medium",
    "typical_entities_hint": ["delivery zones", "courier teams"],
    "typical_metrics_hint": [
      {{"name": "delivery_time", "unit": "minutes"}},
      {{"name": "success_rate", "unit": "%"}}
    ],
    "temporal_granularity_hint": "daily"
  }},
  {{
    "name": "Airport runway utilization and delay propagation",
    "topic": "Transportation & Logistics",
    "complexity_tier": "complex",
    "typical_entities_hint": ["runways", "airlines", "time slots"],
    "typical_metrics_hint": [
      {{"name": "turnaround_time", "unit": "minutes"}},
      {{"name": "delay_minutes", "unit": "minutes"}}
    ],
    "temporal_granularity_hint": "hourly"
  }}
]"""


# ================================================================
# Overlap Detection (§0.4)
# ================================================================

def check_overlap(
    items: list[str],
    threshold: float = 0.80,
) -> list[tuple[str, str, float]]:
    from .overlap_checker import check_overlap as _check
    return _check(items, threshold=threshold)


# ================================================================
# Domain Pool Builder (§0.1–0.5)
# ================================================================

class DomainPool:
    """Orchestrator that builds and caches the full domain taxonomy.

    Intended to be invoked via the build script (run once, offline):
        python pipeline/phase_0/build_domain_pool.py

    The build script reads seed topics from pipeline/phase_0/taxonomy_seed.json,
    calls the LLM to generate subtopics for each topic, deduplicates,
    and writes the result to pipeline/phase_0/domain_pool.json.
    AGPDSPipeline then samples from that compiled pool at runtime.
    """

    def __init__(self, llm_client, pool_path: str = "domain_pool.json",
                 seed_path: Optional[str] = None):
        """
        Args:
            llm_client: LLMClient instance with generate_json() method.
            pool_path: Path to the cached domain pool JSON file.
            seed_path: Optional path to taxonomy_seed.json. If provided,
                       seed topics are loaded from the file. Otherwise the
                       LLM generates topics from scratch.
        """
        self.llm = llm_client
        self.pool_path = Path(pool_path)
        self.seed_path = Path(seed_path) if seed_path else None

    def load_or_build(
        self,
        n_topics: int = 30,
        subtopics_per_topic: int = 7,
        overlap_threshold: float = 0.80,
        force: bool = False, # if True, rebuild even if a cached pool already exists
    ) -> dict:
        """Load from cache if available, otherwise build via LLM.

        This method is idempotent — calling it multiple times will return
        the cached result after the first build.

        Args:
            n_topics: Total number of topics to use. If seed_path is set,
                      this is ignored and all seed topics are used instead.
            subtopics_per_topic: Number of sub-topics per topic.
            overlap_threshold: Cosine similarity threshold for dedup.
            force: If True, rebuild even if a cached pool already exists.

        Returns:
            Domain pool dict matching the output schema (§0.5).
        """
        if not force and self.pool_path.exists():
            with open(self.pool_path) as f:
                pool = json.load(f)
            if self._validate_pool(pool):
                return pool

        pool = self._build(n_topics, subtopics_per_topic, overlap_threshold)
        self._save(pool)
        return pool

    def _build(
        self,
        n_topics: int,
        subtopics_per_topic: int,
        overlap_threshold: float,
    ) -> dict:
        """Build the full domain pool from scratch via LLM calls."""
        # Step 1: Load seed topics
        if self.seed_path and self.seed_path.exists():
            with open(self.seed_path) as f:
                seed_data = json.load(f)
            topics = [d["tier"] for d in seed_data["domains"]]
        else:
            # No seed file: generate all topics from scratch via LLM
            topics = self._generate_topics(n_topics, [])

        # Dedup topics
        overlaps = check_overlap(topics, threshold=overlap_threshold)
        if overlaps:
            drop_set = {pair[1] for pair in overlaps}  # Drop the second item
            topics = [t for t in topics if t not in drop_set]

        # Step 2: Generate sub-topics per topic
        all_domains = []
        for topic in topics:
            subtopics = self._generate_subtopics(
                topic, subtopics_per_topic, existing=[]
            )

            # Dedup within topic
            names = [s["name"] for s in subtopics]
            overlaps = check_overlap(names, threshold=overlap_threshold)
            if overlaps:
                drop_set = {pair[1] for pair in overlaps}
                subtopics = [s for s in subtopics if s["name"] not in drop_set]

            all_domains.extend(subtopics)

        # Step 3: Assign IDs
        all_domains = self._assign_ids(all_domains)

        # Step 4: Build output
        complexity_dist = {}
        topic_coverage = {}
        for d in all_domains:
            tier = d.get("complexity_tier", "unknown")
            complexity_dist[tier] = complexity_dist.get(tier, 0) + 1
            topic = d.get("topic", "unknown")
            topic_coverage[topic] = topic_coverage.get(topic, 0) + 1

        pool = {
            "version": "1.0",
            "generated_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "total_domains": len(all_domains),
            "diversity_score": self._compute_diversity(all_domains),
            "complexity_distribution": complexity_dist,
            "topic_coverage": topic_coverage,
            "domains": all_domains,
        }
        return pool

    def _generate_topics(
        self, n: int, existing: list[str]
    ) -> list[str]:
        """Generate new topics via LLM (§0.2)."""
        user_prompt = TOPIC_USER_PROMPT_TEMPLATE.format(
            n=n, existing_topics=json.dumps(existing)
        )
        response = self.llm.generate_json(
            system=TOPIC_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.9,
            max_tokens=16000,
        )
        if isinstance(response, list):
            return [str(t) for t in response]
        return []

    def _generate_subtopics(
        self, topic: str, n: int, existing: list[str]
    ) -> list[dict]:
        """Generate sub-topics for a topic via LLM (§0.3)."""
        user_prompt = SUBTOPIC_USER_PROMPT_TEMPLATE.format(
            topic=topic,
            n=n,
            existing_subtopics=json.dumps(existing),
        )
        response = self.llm.generate_json(
            system=SUBTOPIC_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.9,
            max_tokens=8192,
        )
        if isinstance(response, list):
            # Ensure topic field is set
            for item in response:
                if isinstance(item, dict):
                    item.setdefault("topic", topic)
            return [d for d in response if isinstance(d, dict)]
        return []

    @staticmethod
    def _assign_ids(domains: list[dict]) -> list[dict]:
        """Add sequential 'dom_XXX' IDs."""
        for i, d in enumerate(domains, start=1):
            d["id"] = f"dom_{i:03d}"
        return domains

    @staticmethod
    def _compute_diversity(domains: list[dict]) -> float:
        """Compute a simple diversity score (0–1).

        Based on how evenly complexity tiers are distributed.
        """
        if not domains:
            return 0.0
        tiers = [d.get("complexity_tier", "") for d in domains]
        unique_tiers = set(tiers)
        if len(unique_tiers) <= 1:
            return 0.0
        counts = [tiers.count(t) for t in unique_tiers]
        total = sum(counts)
        # Normalized entropy
        import math
        entropy = -sum(
            (c / total) * math.log2(c / total) for c in counts if c > 0
        )
        max_entropy = math.log2(len(unique_tiers))
        return round(entropy / max_entropy, 2) if max_entropy > 0 else 0.0

    @staticmethod
    def _validate_pool(pool: dict) -> bool:
        """Basic validation of a loaded pool JSON."""
        return (
            isinstance(pool, dict)
            and "version" in pool
            and "domains" in pool
            and isinstance(pool["domains"], list)
            and len(pool["domains"]) > 0
        )

    def _save(self, pool: dict) -> None:
        """Write pool to disk."""
        self.pool_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pool_path, "w") as f:
            json.dump(pool, f, indent=2, ensure_ascii=False)


# ================================================================
# Domain Sampler (§0.6)
# ================================================================

class DomainSampler:
    """Stratified sampler drawing from the Phase 0 domain pool.

    Draws without replacement. Resets when pool is 80% exhausted.

    Usage:
        sampler = DomainSampler("domain_pool.json")
        domains = sampler.sample(n=3, complexity="medium")
    """

    def __init__(self, pool_path: str, seed: int = 0):
        with open(pool_path) as f:
            data = json.load(f)
        self.pool: list[dict] = data["domains"]
        self.used_ids: set[str] = set()
        self._rng = random.Random(seed)

    def sample(
        self, n: int = 1, complexity: Optional[str] = None, topic: Optional[str] = None
    ) -> list[dict]:
        """Sample n domains without replacement.

        Args:
            n: Number of domains to sample.
            complexity: Optional filter — "simple", "medium", or "complex".
            topic: Optional filter for a specific topic (e.g., "Media & Entertainment").

        Returns:
            List of domain dicts from the pool.
        """
        candidates = [
            d for d in self.pool if d["id"] not in self.used_ids
        ]

        if topic:
            candidates = [
                d for d in candidates
                if d.get("topic") == topic
            ]

        if complexity:
            candidates = [
                d for d in candidates
                if d.get("complexity_tier") == complexity
            ]

        # Reset at 80% exhaustion of the overall pool, or as a fallback when
        # filtered candidates are insufficient to satisfy the request.
        total_pool_size = len(self.pool)
        if len(self.used_ids) >= 0.8 * total_pool_size or len(candidates) < n:
            self.used_ids.clear()
            candidates = self.pool
            if topic:
                candidates = [d for d in candidates if d.get("topic") == topic]
            if complexity:
                candidates = [d for d in candidates if d.get("complexity_tier") == complexity]

        selected = self._rng.sample(candidates, min(n, len(candidates)))
        self.used_ids.update(d["id"] for d in selected)
        return selected

    def reset(self) -> None:
        """Manually reset sampling state."""
        self.used_ids.clear()
