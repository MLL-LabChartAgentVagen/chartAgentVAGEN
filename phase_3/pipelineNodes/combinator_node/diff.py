"""Diff node — subtract two scalars ((S,S) → S)."""

from typing import Any, List, Optional

from .base import ScalarCombinatorNode


class Diff(ScalarCombinatorNode):
    """Subtract two scalars.

    Example: Diff()(cost_A, cost_B) → 1200
    """

    name: str = "Diff"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "How much more is {a_desc} compared to {b_desc}?",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _combine(self, s1: Any, s2: Any) -> Any:
        return s1 - s2
