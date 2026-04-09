"""TrendCompare bridge — compare trend directions of two temporal views."""

from typing import Any, List

import pandas as pd
import numpy as np

from .base import BridgeOperator
from operators.base import OperatorResult


class TrendCompare(BridgeOperator):
    """Compare the temporal trend direction of two views.

    Signature: (V, V) → S
    Both views must have a time axis. Returns a qualitative comparison
    (e.g. "both increasing", "diverging", "both decreasing").

    Example:
        Chart A: month × wait  |  Chart B: month × cost
        TrendCompare(V_a, V_b) → S = "both increasing"
    """

    name: str = "TrendCompare"
    input_type: str = "(V,V)"
    output_type: str = "S"
    compatible_charts: List[str] = ["line_chart", "area_chart"]
    question_templates: List[str] = [
        "Do {series_a} and {series_b} trend in the same direction?",
    ]

    def __init__(self, measure_col: str, time_col: str):
        self.measure_col = measure_col
        self.time_col = time_col

    def execute(self, view_a: pd.DataFrame, view_b: pd.DataFrame, **params: Any) -> OperatorResult:
        trend_a = self._trend_direction(view_a)
        trend_b = self._trend_direction(view_b)

        if trend_a == trend_b:
            result = f"both {trend_a}"
        else:
            result = f"diverging ({trend_a} vs {trend_b})"

        return OperatorResult(result_type="S", value=result)

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
