"""Min node — minimum value in a column (V → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import ScalarNode


class Min(ScalarNode):
    """Return the minimum value of a column.

    Example: Min("cost") → 2100
    """

    name: str = "Min"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "line_chart", "area_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "What is the minimum {measure} of {subject}?",
        "What is the minimum {measure}?",
    ]

    def __init__(self, column: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column

    def _reduce(self, view: pd.DataFrame) -> Any:
        return view[self.column].min()
