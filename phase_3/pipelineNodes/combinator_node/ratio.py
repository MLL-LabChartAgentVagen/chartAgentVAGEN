"""Ratio node — divide two scalars ((S,S) → S)."""

from typing import Any, List, Optional

from .base import ScalarCombinatorNode


class Ratio(ScalarCombinatorNode):
    """Divide two scalars.

    Example: Ratio()(cost_A, avg_cost) → 1.38
    """

    name: str = "Ratio"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "What is the ratio of {a_desc} to {b_desc}?",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _combine(self, s1: Any, s2: Any) -> Any:
        if s2 == 0:
            return float("inf")
        return s1 / s2
