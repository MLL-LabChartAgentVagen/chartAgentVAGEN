"""Sum node — total of a column (V → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import ScalarNode


class Sum(ScalarNode):
    """Return the sum of a column.

    Example: Sum("cost") → 45000
    """

    name: str = "Sum"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "line_chart", "area_chart",
        "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    ]
    question_templates: List[str] = [
        "What is the total {measure} of {subject}?",
        "What is the total {measure}?",
    ]

    def __init__(self, column: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column

    def _reduce(self, view: pd.DataFrame) -> Any:
        return view[self.column].sum()
