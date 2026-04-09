"""Diff combinator — subtract two scalars."""

from typing import Any, List

from .base import ScalarCombinator


class Diff(ScalarCombinator):
    """Subtract two scalars.

    Example: cost_A - cost_B = 1200
    """

    name: str = "Diff"
    compatible_charts: List[str] = []  # chart-independent (S,S → S)
    question_templates: List[str] = [
        "How much more is {a_desc} compared to {b_desc}?",
    ]

    def _combine(self, s1: Any, s2: Any, **params: Any) -> Any:
        return s1 - s2
