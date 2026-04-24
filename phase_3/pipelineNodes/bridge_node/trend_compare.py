"""TrendCompare bridge node — compare trend directions of two temporal views ((V,V) → S)."""

from typing import Any, List, Optional

import pandas as pd
import numpy as np

from .base import BridgeNode
from ..base import NodeResult


class TrendCompare(BridgeNode):
    """Compare the temporal trend direction of two views.

    Signature: (V, V) → S
    Both views must have a time axis.
    Returns a qualitative comparison string.

    Example:
        TrendCompare("wait", "month")(V_a, V_b) → "both increasing"
    """

    name: str = "TrendCompare"
    input_type: str = "(V,V)"
    output_type: str = "S"
    compatible_charts: List[str] = ["line_chart", "area_chart"]
    question_templates: List[str] = [
        "Do {series_a} and {series_b} trend in the same direction?",
    ]

    def __init__(self, measure_col: str, time_col: str,
                 inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.measure_col = measure_col
        self.time_col = time_col

    def _compute(self, view_a: pd.DataFrame, view_b: pd.DataFrame) -> NodeResult:
        trend_a = self._trend_direction(view_a)
        trend_b = self._trend_direction(view_b)
        result = f"both {trend_a}" if trend_a == trend_b else f"diverging ({trend_a} vs {trend_b})"
        return NodeResult(result_type="S", value=result)

    def _trend_direction(self, view: pd.DataFrame) -> str:
        sorted_view = view.sort_values(self.time_col)
        vals = sorted_view[self.measure_col].values
        if len(vals) < 2:
            return "flat"
        slope = np.polyfit(range(len(vals)), vals, 1)[0]
        if slope > 0:
            return "increasing"
        elif slope < 0:
            return "decreasing"
        return "flat"
