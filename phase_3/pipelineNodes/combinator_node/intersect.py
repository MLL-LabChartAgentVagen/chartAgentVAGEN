"""Intersect node — keep rows present in both views ((V,V) → V)."""

from typing import List, Optional

import pandas as pd

from .base import ViewCombinatorNode


class Intersect(ViewCombinatorNode):
    """Keep only rows present in both views.

    Example: Intersect()(top_3_by_cost, top_3_by_wait)
    """

    name: str = "Intersect"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "Those that appear in both {branch_a} and {branch_b},",
    ]
    subject_templates: List[str] = [
        "both {branch_a} and {branch_b}",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _merge(self, v1: pd.DataFrame, v2: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(v1, v2, how="inner").reset_index(drop=True)
