"""Limit operator — keep top-k rows."""

from typing import Any, List

import pandas as pd

from .base import SetOperator


class Limit(SetOperator):
    """Keep top-k rows (assumes view is already sorted).

    Example: Keep the top 3 hospitals
    """

    name: str = "Limit"
    compatible_charts: List[str] = [
        "bar_chart", "grouped_bar_chart", "stacked_bar_chart",
        "scatter_plot", "bubble_chart",
    ]
    question_templates: List[str] = [
        "the top {k}",
        "the bottom {k}",
    ]

    def __init__(self, k: int):
        self.k = k

    def _transform(self, view: pd.DataFrame, **params: Any) -> pd.DataFrame:
        return view.head(self.k)
