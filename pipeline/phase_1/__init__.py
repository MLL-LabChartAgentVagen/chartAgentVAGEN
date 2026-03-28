"""
AGPDS Phase 1: Scenario Contextualization

Provides scenario generation from domain samples and deduplication.
"""

from .scenario_contextualizer import (
    ScenarioContextualizer,
    deduplicate_scenarios,
    SCENARIO_SYSTEM_PROMPT,
    VALID_GRANULARITIES,
)

__all__ = [
    "ScenarioContextualizer",
    "deduplicate_scenarios",
    "SCENARIO_SYSTEM_PROMPT",
    "VALID_GRANULARITIES",
]
