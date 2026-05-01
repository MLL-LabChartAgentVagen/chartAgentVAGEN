"""ValueTransfer bridge node — use a numeric value to filter chart B ((S,V) → V)."""

from typing import Any, List, Optional

import pandas as pd

from .base import BridgeNode
from ..base import NodeResult


class ValueTransfer(BridgeNode):
    """Use a numeric value from chart A as a threshold for chart B.

    Signature: (S, V) → V
    S is a numeric threshold; result is chart B filtered by comparing a column to S.

    Example:
        Chart A → Max → S = 5000
        ValueTransfer("cost", "<")(S, V_b) → rows in B where cost < 5000
    """

    name: str = "ValueTransfer"
    input_type: str = "(S,V)"
    output_type: str = "V"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "In chart B, find entries where {col} {op} {threshold},",
    ]

    def __init__(self, column: str, op: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.column = column
        self.op = op

    def _compute(self, threshold: Any, view_b: pd.DataFrame) -> NodeResult:
        filtered = view_b.query(f"`{self.column}` {self.op} @threshold")
        return NodeResult(result_type="V", value=filtered.reset_index(drop=True))
