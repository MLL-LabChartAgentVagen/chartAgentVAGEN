"""Count operator — number of rows."""

from typing import Any, List

import pandas as pd

from .base import ScalarOperator


ALL_CHARTS = [
    "bar_chart", "grouped_bar_chart", "line_chart", "area_chart",
    "histogram", "box_plot", "violin_plot",
    "pie_chart", "donut_chart", "stacked_bar_chart", "treemap",
    "scatter_plot", "bubble_chart", "heatmap", "radar_chart",
    "waterfall_chart", "funnel_chart",
]


class Count(ScalarOperator):
    """Return the number of rows in the view.

    Example: How many hospitals are there? → 5
    """

    name: str = "Count"
    compatible_charts: List[str] = ALL_CHARTS
    question_templates: List[str] = [
        "How many {entity_plural} are there?",
    ]

    def _reduce(self, view: pd.DataFrame, **params: Any) -> Any:
        return len(view)
