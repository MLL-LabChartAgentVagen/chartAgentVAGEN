"""Intersect view combinator — keep rows present in both views."""

from typing import Any, List

import pandas as pd

from .base import ViewCombinator


class Intersect(ViewCombinator):
    """Keep only rows present in both views.

    Example: Top-3 by cost ∩ Top-3 by wait
    """

    name: str = "Intersect"
    compatible_charts: List[str] = []  # chart-type-agnostic (schema constraint)
    question_templates: List[str] = [
        "Those that appear in both {branch_a} and {branch_b},",
    ]

    def _merge(
        self, v1: pd.DataFrame, v2: pd.DataFrame, **params: Any
    ) -> pd.DataFrame:
        return pd.merge(v1, v2, how="inner").reset_index(drop=True)
