"""GroupBy node — aggregate rows by category (V → V)."""

from typing import Dict, List, Optional

import pandas as pd

from .base import SetNode


class GroupBy(SetNode):
    """Aggregate rows by category.

    Example: GroupBy(["department"], {"cost": "mean"})
    """

    name: str = "GroupBy"
    compatible_charts: List[str] = ["scatter_plot", "bubble_chart"]
    question_templates: List[str] = [
        "Grouped by {cat}, computing {agg} of {measure},",
    ]
    subject_templates: List[str] = [
        "grouped by {cat}",
    ]

    def __init__(self, columns: List[str], agg: Dict[str, str],
                 inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.columns = columns
        self.agg_dict = agg

    def _transform(self, view: pd.DataFrame) -> pd.DataFrame:
        return view.groupby(self.columns).agg(self.agg_dict).reset_index()
