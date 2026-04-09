"""Union view combinator — append rows from both views."""

from typing import Any, List

import pandas as pd

from .base import ViewCombinator


class Union(ViewCombinator):
    """Append all rows from both views, dropping exact duplicates.

    Example: Top-3 hospitals ∪ Bottom-2 hospitals
    """

    name: str = "Union"
    compatible_charts: List[str] = []  # chart-type-agnostic (schema constraint)
    question_templates: List[str] = [
        "Combining {branch_a} and {branch_b},",
    ]

    def _merge(
        self, v1: pd.DataFrame, v2: pd.DataFrame, **params: Any
    ) -> pd.DataFrame:
        return pd.concat([v1, v2]).drop_duplicates().reset_index(drop=True)
