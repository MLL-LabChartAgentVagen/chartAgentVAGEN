"""Min operator — minimum value in a column."""

from typing import Any, List

import pandas as pd

from .base import ScalarOperator


class Min(ScalarOperator):
    """Return the minimum value of a column.

    Example: What is the minimum cost? → 2100
    """

    name: str = "Min"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "line_chart", "area_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "What is the minimum {measure}?",
    ]

    def __init__(self, column: str):
        self.column = column

    def _reduce(self, view: pd.DataFrame, **params: Any) -> Any:
        return view[self.column].min()
