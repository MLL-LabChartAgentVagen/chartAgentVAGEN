"""ValueTransfer bridge — use a numeric value to filter chart B."""

from typing import Any, List

import pandas as pd

from .base import BridgeOperator
from operators.base import OperatorResult


class ValueTransfer(BridgeOperator):
    """Use a numeric value from chart A as a threshold for chart B.

    Signature: (S, V) → V
    The scalar S is a numeric threshold.
    The result is chart B filtered by comparing a column to S.

    Example:
        Chart A → Max → S = 5000
        ValueTransfer(S=5000, op=<, V_b) → V = [rows in B where cost < 5000]
    """

    name: str = "ValueTransfer"
    input_type: str = "(S,V)"
    output_type: str = "V"
    compatible_charts: List[str] = []  # any chart with comparable numeric column
    question_templates: List[str] = [
        "In chart B, find entries where {col} {op} {threshold},",
    ]

    def __init__(self, column: str, op: str):
        self.column = column
        self.op = op  # e.g. ">", "<", "==", ">=", "<="

    def execute(self, threshold: Any, view_b: pd.DataFrame, **params: Any) -> OperatorResult:
        query_str = f"`{self.column}` {self.op} @threshold"
        filtered = view_b.query(query_str)
        return OperatorResult(result_type="V", value=filtered.reset_index(drop=True))
