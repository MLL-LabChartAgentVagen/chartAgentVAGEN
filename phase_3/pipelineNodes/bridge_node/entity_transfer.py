"""EntityTransfer bridge node — look up an entity from chart A in chart B ((S,V) → V)."""

from typing import Any, List, Optional

import pandas as pd

from .base import BridgeNode
from ..base import NodeResult


class EntityTransfer(BridgeNode):
    """Use an entity name from chart A to filter chart B.

    Signature: (S, V) → V
    S is a categorical entity name (e.g. "Xiehe Hospital").
    Result is chart B filtered to rows matching that entity.

    Example:
        Chart A → ArgMax → S = "Xiehe"
        EntityTransfer("hospital")(S, V_b) → rows where hospital == "Xiehe"
    """

    name: str = "EntityTransfer"
    input_type: str = "(S,V)"
    output_type: str = "V"
    compatible_charts: List[str] = []
    question_templates: List[str] = [
        "In chart B, look up {entity},",
    ]

    def __init__(self, cat_col: str, inputs: Optional[List] = None):
        super().__init__(inputs=inputs)
        self.cat_col = cat_col

    def _compute(self, entity: Any, view_b: pd.DataFrame) -> NodeResult:
        filtered = view_b[view_b[self.cat_col] == entity]
        return NodeResult(result_type="V", value=filtered.reset_index(drop=True))
