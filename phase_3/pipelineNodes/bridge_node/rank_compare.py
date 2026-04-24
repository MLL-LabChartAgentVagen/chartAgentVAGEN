"""RankCompare bridge node — compare entity rankings between two views ((V,V) → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import BridgeNode
from ..base import NodeResult


class RankCompare(BridgeNode):
    """Compare entity rankings between two views.

    Signature: (V, V) → S
    Both views must have ranked categorical entities.
    Returns overlap count as a string.

    Example:
        RankCompare("hospital")(top_3_by_cost, top_3_by_satisfaction) → "2 of 3 overlap"
    """

    name: str = "RankCompare"
    input_type: str = "(V,V)"
    output_type: str = "S"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "stacked_bar_chart",
    ]
    question_templates: List[str] = [
        "Do the rankings match between chart A and chart B?",
    ]

    def __init__(self, cat_col: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.cat_col = cat_col

    def _compute(self, view_a: pd.DataFrame, view_b: pd.DataFrame) -> NodeResult:
        entities_a = set(view_a[self.cat_col].values)
        entities_b = set(view_b[self.cat_col].values)
        overlap = entities_a & entities_b
        total = max(len(entities_a), len(entities_b))
        result = f"{len(overlap)} of {total} overlap"
        return NodeResult(result_type="S", value=result)
