"""
AGPDS Phase 1: Scenario Contextualization

Provides scenario generation from domain samples and deduplication.
"""

from .scenario_contextualizer import (
    ScenarioContextualizer,
    SCENARIO_SYSTEM_PROMPT,
    TIER_TARGET_ROWS,
    VALID_GRANULARITIES,
)
from .dedup import deduplicate_scenario_records
from .types import Metric, ScenarioContext, ScenarioRecord

__all__ = [
    "ScenarioContextualizer",
    "deduplicate_scenario_records",
    "Metric",
    "ScenarioContext",
    "ScenarioRecord",
    "SCENARIO_SYSTEM_PROMPT",
    "TIER_TARGET_ROWS",
    "VALID_GRANULARITIES",
]
