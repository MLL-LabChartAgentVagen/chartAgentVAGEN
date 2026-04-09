"""Ratio combinator — divide two scalars."""

from typing import Any, List

from .base import ScalarCombinator


class Ratio(ScalarCombinator):
    """Divide two scalars.

    Example: cost_A / avg_cost = 1.38
    """

    name: str = "Ratio"
    compatible_charts: List[str] = []  # chart-independent (S,S → S)
    question_templates: List[str] = [
        "What is the ratio of {a_desc} to {b_desc}?",
    ]

    def _combine(self, s1: Any, s2: Any, **params: Any) -> Any:
        if s2 == 0:
            return float("inf")
        return s1 / s2
