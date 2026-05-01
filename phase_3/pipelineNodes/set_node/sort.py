"""Sort node — order rows by a column (V → V)."""

from typing import List, Optional

import pandas as pd

from .base import SetNode


class Sort(SetNode):
    """Order rows by a column.

    Example: Sort("cost", ascending=False)
    """

    name: str = "Sort"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "stacked_bar_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "Ranked by {measure} in {direction} order,",
    ]
    subject_templates: List[str] = [
        "sorted by {measure} {direction}",
    ]

    def __init__(self, column: str, ascending: bool = False,
                 inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column
        self.ascending = ascending

    def _transform(self, view: pd.DataFrame) -> pd.DataFrame:
        return view.sort_values(self.column, ascending=self.ascending)
