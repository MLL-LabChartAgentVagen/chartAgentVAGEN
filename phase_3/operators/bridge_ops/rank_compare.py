"""RankCompare bridge — compare entity rankings between two views."""

from typing import Any, List

import pandas as pd

from .base import BridgeOperator
from operators.base import OperatorResult


class RankCompare(BridgeOperator):
    """Compare entity rankings between two views.

    Signature: (V, V) → S
    Both views must have ranked categorical entities.
    Returns overlap count or rank delta.

    Example:
        Chart A: top-3 hospitals by cost
        Chart B: top-3 hospitals by satisfaction
        RankCompare(V_a, V_b) → S = "2 of 3 overlap"
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

    def __init__(self, cat_col: str):
        self.cat_col = cat_col

    def execute(self, view_a: pd.DataFrame, view_b: pd.DataFrame, **params: Any) -> OperatorResult:
        entities_a = set(view_a[self.cat_col].values)
        entities_b = set(view_b[self.cat_col].values)
        overlap = entities_a & entities_b
        total = max(len(entities_a), len(entities_b))
        result = f"{len(overlap)} of {total} overlap"
        return OperatorResult(result_type="S", value=result)
