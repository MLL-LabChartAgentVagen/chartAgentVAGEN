"""ArgMin operator — entity with the lowest value."""

from typing import Any, List

import pandas as pd

from .base import ScalarOperator


class ArgMin(ScalarOperator):
    """Return the entity (category value) with the lowest measure.

    Example: Which hospital has the lowest cost? → "People's #2"
    """

    name: str = "ArgMin"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "bubble_chart", "radar_chart",
        "waterfall_chart", "funnel_chart", "heatmap",
    ]
    question_templates: List[str] = [
        "Which {cat} has the lowest {measure}?",
    ]

    def __init__(self, measure_col: str, cat_col: str):
        self.measure_col = measure_col
        self.cat_col = cat_col

    def _reduce(self, view: pd.DataFrame, **params: Any) -> Any:
        idx = view[self.measure_col].idxmin()
        return view.loc[idx, self.cat_col]
