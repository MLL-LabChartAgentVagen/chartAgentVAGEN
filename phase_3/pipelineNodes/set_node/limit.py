"""Limit node — keep top-k rows (V → V)."""

from typing import List, Optional

import pandas as pd

from .base import SetNode


class Limit(SetNode):
    """Keep top-k rows (assumes view is already sorted).

    Example: Limit(3)
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
    subject_templates: List[str] = [
        "top {k}",
    ]

    def __init__(self, k: int, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.k = k

    def _transform(self, view: pd.DataFrame) -> pd.DataFrame:
        return view.head(self.k)
