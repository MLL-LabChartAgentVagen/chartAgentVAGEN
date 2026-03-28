"""
AGPDS Phase 1: Scenario Contextualization

Bridges the real world and the simulation engine. Generates semantic anchors
(scenario contexts) that constrain Phase 2's data generation to be realistic,
diverse, and domain-grounded.

Components:
- ScenarioContextualizer: LLM-driven scenario generation from domain samples
- deduplicate_scenarios: Embedding-based scenario deduplication

Reference: phase_1.md
"""

import json
from typing import Optional, Callable


# ================================================================
# Prompts (§1.2)
# ================================================================

SCENARIO_SYSTEM_PROMPT = """\
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
6. "target_rows": Recommended row count for the physical fact table (100-3000).
7. Ground all numbers, entities, and time windows in plausible real-world conditions.
   The scenario must read as if it were a real dataset from a real organization.
8. Output strictly valid JSON with no additional commentary."""

SCENARIO_USER_PROMPT_TEMPLATE = """\
Generate a concrete, realistic data scenario for the following domain.

Domain metadata:
{domain_json}

Use the hints (typical_entities_hint, typical_metrics_hint, temporal_granularity_hint)
as soft guidance — you may adapt or override them when the specific scenario demands
different specifics, but stay faithful to the domain's scope and complexity tier.

=== ONE-SHOT EXAMPLE ===
Domain metadata:
{{
  "name": "Urban rail transit scheduling",
  "topic": "Transportation & Logistics",
  "complexity_tier": "complex",
  "typical_entities_hint": ["metro lines", "stations", "time slots"],
  "typical_metrics_hint": [
    {{"name": "ridership", "unit": "10k passengers"}},
    {{"name": "on_time_rate", "unit": "%"}}
  ],
  "temporal_granularity_hint": "daily"
}}

Output:
{{
  "scenario_title": "2024 H1 Shanghai Metro Ridership & Operations Log",
  "data_context": "Shanghai Transport Commission collected daily ridership and \
operational performance data across core metro lines over January–June 2024 \
to optimize peak-hour scheduling and identify maintenance bottlenecks.",
  "temporal_granularity": "daily",
  "key_entities": ["Line 1 (Xinzhuang–Fujin Rd)", "Line 2 (Pudong Intl Airport–East Xujing)",
                    "Line 8 (Shiguang Rd–Shendu Hwy)", "Line 9 (Songjiang South–Caolu)",
                    "Line 10 (Hongqiao Airport–New Jiangwan City)"],
  "key_metrics": [
    {{"name": "daily_ridership", "unit": "10k passengers", "range": [5, 120]}},
    {{"name": "on_time_rate", "unit": "%", "range": [85.0, 99.9]}},
    {{"name": "equipment_failures", "unit": "count", "range": [0, 5]}}
  ],
  "target_rows": 900
}}

=== YOUR TASK ===
Output:"""


# ================================================================
# Scenario Contextualizer
# ================================================================

VALID_GRANULARITIES = {
    "hourly", "daily", "weekly", "monthly", "quarterly", "yearly"
}


class ScenarioContextualizer:
    """Generate structured scenario contexts from domain samples.

    Refactored from NodeA_TopicAgent — keeps the orchestration pattern
    (prompt builder + diversity tracker + validator + retry) but replaces
    input/output schema and prompt content for AGPDS Phase 1.

    Usage:
        ctx = ScenarioContextualizer(llm_client)
        scenario = ctx.generate(domain_sample)
    """

    def __init__(
        self,
        llm_client,
        diversity_tracker: Optional[dict] = None,
        max_retries: int = 2,
    ):
        """
        Args:
            llm_client: LLMClient instance with generate_json() method.
            diversity_tracker: Shared tracker dict for cross-batch dedup.
            max_retries: Number of LLM retries on validation failure.
        """
        self.llm = llm_client
        self.diversity_tracker = diversity_tracker or {
            "used_titles": [],
            "used_contexts": [],
        }
        self.max_retries = max_retries

    def generate(self, domain_sample: dict) -> dict:
        """Generate a scenario context from a Phase 0 domain sample.

        Args:
            domain_sample: A single domain dict from DomainSampler.sample().
                Must contain: name, topic, complexity_tier, and hint fields.

        Returns:
            Scenario dict with: scenario_title, data_context, key_entities,
            key_metrics, temporal_granularity, target_rows.

        Raises:
            ValueError: If all retries fail validation.
        """
        system_prompt = SCENARIO_SYSTEM_PROMPT
        user_prompt = self._build_user_prompt(domain_sample)

        last_errors = []
        for attempt in range(self.max_retries + 1):
            response = self.llm.generate_json(
                system=system_prompt,
                user=user_prompt,
                temperature=1.0,
            )

            is_valid, errors = self.validate_output(response)
            if is_valid:
                self._update_tracker(response)
                return response

            last_errors = errors

        # Soft failure — return last response with warnings
        import warnings
        warnings.warn(
            f"Scenario validation warnings after {self.max_retries + 1} "
            f"attempts: {last_errors}"
        )
        if isinstance(response, dict):
            response["_validation_warnings"] = last_errors
            self._update_tracker(response)
            return response

        raise ValueError(
            f"Failed to generate valid scenario after "
            f"{self.max_retries + 1} attempts. Errors: {last_errors}"
        )

    def _build_user_prompt(self, domain_sample: dict) -> str:
        """Build the user prompt with domain metadata injection."""
        domain_json = json.dumps(domain_sample, indent=2, ensure_ascii=False)
        return SCENARIO_USER_PROMPT_TEMPLATE.format(domain_json=domain_json)

    @staticmethod
    def validate_output(
        response: dict,
    ) -> tuple[bool, list[str]]:
        """Validate scenario output structure and value ranges.

        Args:
            response: LLM response dict.

        Returns:
            (is_valid, errors) tuple.
        """
        if not isinstance(response, dict):
            return False, ["Response is not a dict"]

        errors = []

        # Required fields
        required = [
            "scenario_title", "data_context", "key_entities",
            "key_metrics", "temporal_granularity", "target_rows",
        ]
        for field in required:
            if field not in response:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Type and range checks
        entities = response["key_entities"]
        if not isinstance(entities, list):
            errors.append("key_entities must be a list")
        elif not (3 <= len(entities) <= 8):
            errors.append(
                f"key_entities: expected 3-8 items, got {len(entities)}"
            )

        metrics = response["key_metrics"]
        if not isinstance(metrics, list):
            errors.append("key_metrics must be a list")
        elif not (2 <= len(metrics) <= 5):
            errors.append(
                f"key_metrics: expected 2-5 items, got {len(metrics)}"
            )

        granularity = response["temporal_granularity"]
        if granularity not in VALID_GRANULARITIES:
            errors.append(
                f"Invalid temporal_granularity: '{granularity}'. "
                f"Must be one of {sorted(VALID_GRANULARITIES)}"
            )

        target_rows = response["target_rows"]
        if not isinstance(target_rows, (int, float)):
            errors.append(f"target_rows must be numeric, got {type(target_rows)}")
        elif not (100 <= target_rows <= 3000):
            errors.append(
                f"target_rows out of range: {target_rows} (expected 100-3000)"
            )

        # Scenario title should be non-empty
        if not response.get("scenario_title", "").strip():
            errors.append("scenario_title is empty")

        # Data context should be non-empty
        if not response.get("data_context", "").strip():
            errors.append("data_context is empty")

        return len(errors) == 0, errors

    def _update_tracker(self, scenario: dict) -> None:
        """Update diversity tracker with the generated scenario."""
        title = scenario.get("scenario_title", "")
        context = scenario.get("data_context", "")
        if title:
            self.diversity_tracker["used_titles"].append(title)
        if context:
            self.diversity_tracker["used_contexts"].append(context)


# ================================================================
# Scenario Deduplication (§1.3)
# ================================================================

def deduplicate_scenarios(
    scenarios: list[dict],
    threshold: float = 0.85,
) -> list[dict]:
    """Remove near-duplicate scenarios based on data_context similarity.

    Reuses Phase 0's check_overlap function on data_context fields.

    Args:
        scenarios: List of scenario dicts (each must have "data_context").
        threshold: Cosine similarity threshold for dedup.

    Returns:
        Filtered list with near-duplicates removed (keeps earlier scenario).
    """
    from pipeline.phase_0.domain_pool import check_overlap

    contexts = [s.get("data_context", "") for s in scenarios]
    overlaps = check_overlap(contexts, threshold=threshold)

    # Collect indices to drop (keep the earlier-generated scenario)
    context_to_idx = {ctx: i for i, ctx in enumerate(contexts)}
    drop_indices: set[int] = set()
    for ctx_a, ctx_b, sim in overlaps:
        drop_indices.add(context_to_idx[ctx_b])  # Drop the later one

    return [s for i, s in enumerate(scenarios) if i not in drop_indices]
