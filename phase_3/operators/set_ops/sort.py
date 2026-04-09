"""Sort operator — order rows by a column."""

from typing import Any, List

import pandas as pd

from .base import SetOperator


class Sort(SetOperator):
    """Order rows by a column.

    Example: Sort hospitals by cost descending
    """

    name: str = "Sort"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "stacked_bar_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "Ranked by {measure} in {direction} order,",
    ]

    def __init__(self, column: str, ascending: bool = False):
        self.column = column
        self.ascending = ascending

    def _transform(self, view: pd.DataFrame, **params: Any) -> pd.DataFrame:
        return view.sort_values(self.column, ascending=self.ascending)
