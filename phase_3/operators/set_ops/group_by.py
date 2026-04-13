"""GroupBy operator — aggregate rows by category."""

from typing import Any, Dict, List

import pandas as pd

from .base import SetOperator


class GroupBy(SetOperator):
    """Aggregate rows by category.

    Example: Group by department, compute AVG(cost)
    """

    name: str = "GroupBy"
    compatible_charts: List[str] = ["scatter_plot", "bubble_chart"]
    question_templates: List[str] = [
        "Grouped by {cat}, computing {agg} of {measure},",
    ]

    def __init__(self, columns: List[str], agg: Dict[str, str]):
        self.columns = columns
        self.agg_dict = agg  # e.g. {"cost": "mean"}

    def _transform(self, view: pd.DataFrame, **params: Any) -> pd.DataFrame:
        return view.groupby(self.columns).agg(self.agg_dict).reset_index()
