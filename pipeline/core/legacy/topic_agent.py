"""
NodeA_TopicAgent — Topic concept generation within a user-specified category.

Salvaged from generation_pipeline.py (L214–319 prompt, L626–799 class).

Architecture:
- Prompt builder (system + user prompts with diversity hints)
- Diversity tracker (avoids topic repetition in batch generation)
- Output validator (field/type/similarity checks)
- State updater (__call__ protocol)

The class skeleton and plumbing (LLM call, retry, state mutation) remain as-is.
The *content* (prompt, output schema, dedup method) will be rewritten for AGPDS
Phase 1 integration (Subtask 2 in agpds_salvage_and_roadmap.md).
"""

from typing import Optional

from .utils import META_CATEGORIES


# =============================================================================
# System Prompt
# =============================================================================

PROMPT_NODE_A_TOPIC_AGENT = """You are a Topic Generation Agent for a chart data synthesis pipeline.

## Your Role
Generate diverse, realistic topics for data visualization WITHIN the assigned category.

## CRITICAL: Autonomous Diversity Strategy

To avoid model collapse and ensure maximum diversity, YOU MUST autonomously vary these dimensions:

1. **Scale Dimension**:
   - Micro: Individual items, specific products, single entities
   - Meso: Cities, companies, categories
   - Macro: Countries, industries, global comparisons
   - Meta: Cross-domain, abstract metrics

2. **Temporal Dimension**:
   - Historical: Pre-2010, decade-specific analysis
   - Current: 2020-2025, recent trends
   - Projected: Future predictions, forecasts
   - Timeless: Universal patterns, non-temporal data

3. **Geographic Scope**:
   - Local: City-level, regional
   - National: Country-specific
   - International: Cross-country comparisons
   - Global: Worldwide aggregates

4. **Specificity Level**:
   - Mainstream: Well-known entities, popular topics
   - Specialized: Industry-specific, technical domains
   - Niche: Obscure but valid topics, emerging areas
   - Cross-disciplinary: Unexpected combinations

5. **Metric Types**:
   - Counts: Absolute numbers, quantities
   - Rates: Percentages, ratios, per-capita
   - Monetary: Revenue, costs, valuations
   - Physical: Weights, distances, volumes
   - Temporal: Durations, frequencies

**For EACH generation**: Consciously select a DIFFERENT combination of these dimensions to create unique topics within the assigned category.

**Example Variations Within "Media & Entertainment"**:
- Micro + Current + Niche: "Average watch time of vertical short-form videos by creator tier (2024)"
- Macro + Historical + Mainstream: "Global box office revenue by film genre (2010-2020)"
- Meso + Projected + Specialized: "Podcast advertising revenue projections by category (2025-2027)"

## Assigned Category (User-Specified)
**{category_name}** (ID: {category_id})

You MUST generate a topic that belongs to this category.

## Output Format
Return a JSON object with these exact keys:
{{
    "semantic_concept": "<specific topic, 3-8 words>",
    "topic_description": "<one sentence explaining what data would be visualized>",
    "suggested_entities": ["<entity1>", "<entity2>", ...],  // 8-12 entities
    "suggested_metrics": ["<metric1>", "<metric2>", "<metric3>"],  // 2-3 quantifiable metrics
    "domain_context": "<brief domain background for realistic data generation>"
}}

## Diversity Requirements (Critical: Avoid Repetitive Topics)
- Vary between micro (individual items) and macro (countries, industries) scales
- Include both well-known and obscure topics within this category
- Balance between contemporary (2020s) and timeless topics
- Consider international perspectives, not just US-centric
- Generate UNIQUE topics - avoid repeating similar concepts

## Examples of Good Semantic Concepts for Different Categories

### Media & Entertainment
- "Streaming platform subscriber growth 2020-2024"
- "Box office revenue by film genre in Asia"
- "Podcast listening hours by age demographic"

### Geography & Demography
- "Urban population density in European capitals"
- "Migration patterns of coastal cities"
- "Median household income by region"

### Business & Industry
- "Market capitalization of semiconductor companies"
- "Supply chain disruptions by industry sector"
- "Corporate carbon emissions by Fortune 500 companies"

### Health & Medicine
- "Hospital bed capacity by metropolitan area"
- "Vaccination rates across different age groups"
- "Mental health service availability by country"

### Education & Academia
- "University research funding by discipline"
- "Student-teacher ratios in international schools"
- "Graduate employment rates by major"

### Technology & Computing
- "Cloud service market share by provider"
- "Programming language popularity trends"
- "Semiconductor chip production capacity"

## Anti-patterns to Avoid
- Generic concepts: "Sales data", "Population statistics"
- Overly broad: "Technology trends", "Economic indicators"
- Fictional: Made-up companies, imaginary species
- Repetitive: Topics too similar to recently generated ones
"""


# =============================================================================
# NodeA_TopicAgent
# =============================================================================

class NodeA_TopicAgent:
    """
    Node A: Topic Concept Generation (User-Specified Category Version)

    Responsibilities:
    - Generate semantic concept within user-specified category
    - Provide entity and metric suggestions
    - Provide domain context for downstream data generation
    - Maintain diversity tracker to ensure topic variety in batch generation
    """

    def __init__(self, llm_client, diversity_tracker: Optional[dict] = None):
        self.llm = llm_client
        self.diversity_tracker = diversity_tracker or {
            "used_concepts": [],
            "used_entities": []
        }

    def get_system_prompt(self, category_id: int, category_name: str) -> str:
        """Generate system prompt for specified category."""
        return PROMPT_NODE_A_TOPIC_AGENT.format(
            category_id=category_id,
            category_name=category_name
        )

    def get_user_prompt(self, constraints: Optional[dict] = None) -> str:
        """Generate user prompt with constraints and diversity hints."""
        prompt = (
            "Generate a new, unique topic for chart data synthesis "
            "within the assigned category."
        )

        # Add constraints
        if constraints:
            if constraints.get("avoid_concepts"):
                recent_concepts = constraints["avoid_concepts"][-10:]
                if recent_concepts:
                    prompt += f"\n\n**AVOID these recently used concepts:**\n"
                    for concept in recent_concepts:
                        prompt += f"- {concept}\n"

            if constraints.get("theme_hint"):
                prompt += f"\n\n**Theme suggestion:** {constraints['theme_hint']}"

            if constraints.get("scale_preference"):
                prompt += f"\n\n**Scale preference:** {constraints['scale_preference']}"

        # Enhanced diversity hints with anti-repetition context
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-10:]
        if recent_concepts:
            prompt += (
                "\n\n**Context: Recently generated concepts "
                "(for awareness, not constraints):**"
            )
            for i, concept in enumerate(recent_concepts[-5:], 1):
                prompt += f"\n  {i}. {concept}"

            prompt += (
                "\n\n**Your task**: Generate a concept that explores a "
                "DIFFERENT aspect of the category."
            )
            prompt += (
                "\n- Use a different scale (micro/meso/macro) than "
                "recent examples"
            )
            prompt += "\n- Choose a different time period or geographic focus"
            prompt += "\n- Select different metric types or entity categories"
            prompt += (
                "\n\nDue to your stochastic sampling (temperature > 1.0), "
                "naturally vary the theme, scale, and specificity."
            )

        return prompt

    def validate_output(
        self, response: dict, category_name: str
    ) -> tuple[bool, list[str]]:
        """Validate Node A output."""
        errors = []

        required_fields = [
            "semantic_concept", "topic_description",
            "suggested_entities", "suggested_metrics", "domain_context"
        ]

        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")

        if "suggested_entities" in response:
            if not isinstance(response["suggested_entities"], list):
                errors.append("suggested_entities must be a list")
            elif len(response["suggested_entities"]) < 8:
                errors.append(
                    f"Need at least 8 entities, got "
                    f"{len(response['suggested_entities'])}"
                )

        if "suggested_metrics" in response:
            if not isinstance(response["suggested_metrics"], list):
                errors.append("suggested_metrics must be a list")
            elif len(response["suggested_metrics"]) < 2:
                errors.append("Need at least 2 metrics")

        # Check for topic repetition (substring similarity)
        semantic_concept = response.get("semantic_concept", "")
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-10:]

        for recent in recent_concepts:
            if (semantic_concept.lower() in recent.lower()
                    or recent.lower() in semantic_concept.lower()):
                errors.append(f"Concept too similar to recent: '{recent}'")
                break

        return len(errors) == 0, errors

    def __call__(
        self,
        state: dict,
        category_id: int,
        category_name: str,
        constraints: Optional[dict] = None
    ) -> dict:
        """
        Execute Node A and update state.

        Args:
            state: Pipeline state dict
            category_id: User-specified category ID (1-30)
            category_name: User-specified category name
            constraints: Optional constraints
                - avoid_concepts: list[str] - Concepts to avoid
                - theme_hint: str - Theme suggestion
                - scale_preference: str - e.g. "micro", "macro"

        Returns:
            Updated state dict
        """
        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}. Must be between 1 and 30."
            )

        if category_name not in META_CATEGORIES:
            raise ValueError(
                f"Invalid category_name: {category_name}. "
                f"Must be one of the 30 predefined categories."
            )

        # Prepare constraints (including info from diversity tracker)
        full_constraints = constraints or {}
        if "avoid_concepts" not in full_constraints:
            full_constraints["avoid_concepts"] = \
                self.diversity_tracker.get("used_concepts", [])

        # Call LLM to generate topic
        response = self.llm.generate_json(
            system=self.get_system_prompt(category_id, category_name),
            user=self.get_user_prompt(full_constraints),
            temperature=1.2  # High temperature for maximum topic diversity
        )

        # Validate output
        is_valid, errors = self.validate_output(response, category_name)
        if not is_valid:
            print(f"Warning: Node A validation issues: {errors}")

        # Update diversity tracker
        self.diversity_tracker["used_concepts"].append(
            response.get("semantic_concept", "")
        )
        self.diversity_tracker["used_entities"].extend(
            response.get("suggested_entities", [])[:3]
        )

        # Update state
        state["category_id"] = category_id
        state["category_name"] = category_name
        state["semantic_concept"] = response.get("semantic_concept", "")
        state["topic_description"] = response.get("topic_description", "")

        # Internal variables for downstream nodes
        state["_suggested_entities"] = response.get("suggested_entities", [])
        state["_suggested_metrics"] = response.get("suggested_metrics", [])
        state["_domain_context"] = response.get("domain_context", "")

        return state
