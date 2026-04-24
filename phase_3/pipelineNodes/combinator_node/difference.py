"""Difference node — rows in V_a but not in V_b ((V,V) → V)."""

from typing import List, Optional

import pandas as pd

from .base import ViewCombinatorNode


class Difference(ViewCombinatorNode):
    """Keep rows in the first view that are not in the second view.

    Example: Difference()(top_3_by_cost, top_3_by_wait)
    """

    name: str = "Difference"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "Those in {branch_a} but not in {branch_b},",
    ]
    subject_templates: List[str] = [
        "{branch_a} but not {branch_b}",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _merge(self, v1: pd.DataFrame, v2: pd.DataFrame) -> pd.DataFrame:
        merged = v1.merge(v2, how="left", indicator=True)
        result = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
        return result.reset_index(drop=True)
