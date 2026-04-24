"""Union node — append rows from both views ((V,V) → V)."""

from typing import List, Optional

import pandas as pd

from .base import ViewCombinatorNode


class Union(ViewCombinatorNode):
    """Append all rows from both views, dropping exact duplicates.

    Example: Union()(top_3, bottom_2)
    """

    name: str = "Union"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "Combining {branch_a} and {branch_b},",
    ]
    subject_templates: List[str] = [
        "{branch_a} or {branch_b}",
    ]

    def __init__(self, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)

    def _merge(self, v1: pd.DataFrame, v2: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([v1, v2]).drop_duplicates().reset_index(drop=True)
