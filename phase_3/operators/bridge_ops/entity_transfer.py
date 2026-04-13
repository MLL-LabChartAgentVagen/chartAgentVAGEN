"""EntityTransfer bridge — look up an entity from chart A in chart B."""

from typing import Any, List

import pandas as pd

from .base import BridgeOperator
from operators.base import OperatorResult


class EntityTransfer(BridgeOperator):
    """Use an entity name from chart A to filter chart B.

    Signature: (S, V) → V
    The scalar S is a categorical entity name (e.g. "Xiehe Hospital").
    The result is chart B filtered to rows matching that entity.

    Example:
        Chart A → ArgMax → S = "Xiehe"
        EntityTransfer(S="Xiehe", V_b) → V = [row where hospital="Xiehe" in B]
    """

    name: str = "EntityTransfer"
    input_type: str = "(S,V)"
    output_type: str = "V"
    compatible_charts: List[str] = []  # any chart with a shared categorical column
    question_templates: List[str] = [
        "In chart B, look up {entity},",
    ]

    def __init__(self, cat_col: str):
        self.cat_col = cat_col

    def execute(self, entity: Any, view_b: pd.DataFrame, **params: Any) -> OperatorResult:
        filtered = view_b[view_b[self.cat_col] == entity]
        return OperatorResult(result_type="V", value=filtered.reset_index(drop=True))
