"""ValueAt node — read a value from a single-row view (V → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import ScalarNode


ALL_CHARTS = [
    "bar_chart", "grouped_bar_chart", "line_chart", "area_chart",
    "histogram", "box_plot", "violin_plot",
    "pie_chart", "donut_chart", "stacked_bar_chart", "treemap",
    "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    "waterfall_chart", "funnel_chart",
]


class ValueAt(ScalarNode):
    """Read a cell value from the first row of a (typically single-row) view.

    Example: ValueAt("cost") → 6200
    """

    name: str = "ValueAt"
    compatible_charts: List[str] = ALL_CHARTS
    question_templates: List[str] = [
        "For {subject}, what is {entity}'s {measure}?",
        "What is {entity}'s {measure}?",
    ]

    def __init__(self, column: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column

    def _reduce(self, view: pd.DataFrame) -> Any:
        return view.iloc[0][self.column]
