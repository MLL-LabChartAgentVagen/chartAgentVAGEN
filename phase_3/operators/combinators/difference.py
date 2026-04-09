"""Difference view combinator — rows in V_a but not in V_b."""

from typing import Any, List

import pandas as pd

from .base import ViewCombinator


class Difference(ViewCombinator):
    """Keep rows in the first view that are not in the second view.

    Example: Top-3 by cost − Top-3 by wait
    """

    name: str = "Difference"
    compatible_charts: List[str] = []  # chart-type-agnostic (schema constraint)
    question_templates: List[str] = [
        "Those in {branch_a} but not in {branch_b},",
    ]

    def _merge(
        self, v1: pd.DataFrame, v2: pd.DataFrame, **params: Any
    ) -> pd.DataFrame:
        merged = v1.merge(v2, how="left", indicator=True)
        result = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
        return result.reset_index(drop=True)
