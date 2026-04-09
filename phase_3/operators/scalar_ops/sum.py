"""Sum operator — total of a column."""

from typing import Any, List

import pandas as pd

from .base import ScalarOperator


class Sum(ScalarOperator):
    """Return the sum of a column.

    Example: What is the total cost? → 45000
    """

    name: str = "Sum"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "line_chart", "area_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "What is the total {measure}?",
    ]

    def __init__(self, column: str):
        self.column = column

    def _reduce(self, view: pd.DataFrame, **params: Any) -> Any:
        return view[self.column].sum()
