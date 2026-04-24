"""Count node — number of rows (V → S)."""

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


class Count(ScalarNode):
    """Return the number of rows in the view.

    Example: Count() → 5
    """

    name: str = "Count"
    compatible_charts: List[str] = ALL_CHARTS
    question_templates: List[str] = [
        "How many {entity_plural} in {subject} are there?",
        "How many {entity_plural} are there?",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _reduce(self, view: pd.DataFrame) -> Any:
        return len(view)
