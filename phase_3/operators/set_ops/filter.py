"""Filter operator — keep rows matching a condition."""

from typing import Any, List

import pandas as pd

from .base import SetOperator


ALL_CHARTS = [
    "bar_chart", "grouped_bar_chart", "line_chart", "area_chart",
    "histogram", "box_plot", "violin_plot",
    "pie_chart", "donut_chart", "stacked_bar_chart", "treemap",
    "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    "waterfall_chart", "funnel_chart",
]


class Filter(SetOperator):
    """Keep rows matching a condition.

    Example: Keep only rows where hospital = "Xiehe"
    """

    name: str = "Filter"
    compatible_charts: List[str] = ALL_CHARTS
    question_templates: List[str] = [
        "Among the {entity} entries,",
        "For rows where {col} {op} {val},",
    ]

    def __init__(self, column: str, op: str, value: Any):
        self.column = column
        self.op = op
        self.value = value

    def _transform(self, view: pd.DataFrame, **params: Any) -> pd.DataFrame:
        query_str = f"`{self.column}` {self.op} @self.value"
        return view.query(query_str)
