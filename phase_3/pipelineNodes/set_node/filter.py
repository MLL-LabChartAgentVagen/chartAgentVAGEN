"""Filter node — keep rows matching a condition (V → V)."""

from typing import Any, List, Optional

import pandas as pd

from .base import SetNode


ALL_CHARTS = [
    "bar_chart", "grouped_bar_chart", "line_chart", "area_chart",
    "histogram", "box_plot", "violin_plot",
    "pie_chart", "donut_chart", "stacked_bar_chart", "treemap",
    "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    "waterfall_chart", "funnel_chart",
]


class Filter(SetNode):
    """Keep rows matching a condition.

    Example: Filter("hospital", "==", "Xiehe")
    """

    name: str = "Filter"
    compatible_charts: List[str] = ALL_CHARTS
    question_templates: List[str] = [
        "Among the {entity} entries,",
        "For rows where {col} {op} {val},",
    ]
    subject_templates: List[str] = [
        "{col} {op} {val}",
    ]

    def __init__(self, column: str, op: str, value: Any,
                 inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column
        self.op = op
        self.value = value

    def _transform(self, view: pd.DataFrame) -> pd.DataFrame:
        return view.query(f"`{self.column}` {self.op} @self.value")
