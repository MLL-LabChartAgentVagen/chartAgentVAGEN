"""ArgMin node — entity with the lowest value (V → S)."""

from typing import Any, List, Optional

import pandas as pd

from .base import ScalarNode


class ArgMin(ScalarNode):
    """Return the entity (category value) with the lowest measure.

    Example: ArgMin("cost", "hospital") → "People's #2"
    """

    name: str = "ArgMin"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "pie_chart", "donut_chart",
        "stacked_bar_chart", "bubble_chart", "radar_chart",
        "waterfall_chart", "funnel_chart", "heatmap",
    ]
    question_templates: List[str] = [
        "Among {subject}, which {cat} has the lowest {measure}?",
        "Which {cat} has the lowest {measure}?",
    ]

    def __init__(self, measure_col: str, cat_col: str,
                 inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.measure_col = measure_col
        self.cat_col = cat_col

    def _reduce(self, view: pd.DataFrame) -> Any:
        idx = view[self.measure_col].idxmin()
        return view.loc[idx, self.cat_col]
