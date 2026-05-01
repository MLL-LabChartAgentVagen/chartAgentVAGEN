"""Max node — maximum value in a column (V → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import ScalarNode


class Max(ScalarNode):
    """Return the maximum value of a column.

    Example: Max("cost") → 6200
    """

    name: str = "Max"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "line_chart", "area_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "What is the maximum {measure} of {subject}?",
        "What is the maximum {measure}?",
    ]

    def __init__(self, column: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column

    def _reduce(self, view: pd.DataFrame) -> Any:
        return view[self.column].max()
