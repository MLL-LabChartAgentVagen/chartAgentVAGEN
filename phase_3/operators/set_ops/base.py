"""Base class for set operators (V → V)."""

from abc import abstractmethod
from typing import Any

import pandas as pd

from operators.base import Operator, OperatorResult


class SetOperator(Operator):
    """Abstract base for operators that transform a view into another view.

    Signature: V → V
    """

    input_type: str = "V"
    output_type: str = "V"

    def execute(self, view: pd.DataFrame, **params: Any) -> OperatorResult:
        """Apply the transformation and wrap in an OperatorResult(V)."""
        result_df = self._transform(view, **params)
        return OperatorResult(result_type="V", value=result_df)

    @abstractmethod
    def _transform(self, view: pd.DataFrame, **params: Any) -> pd.DataFrame:
        """Subclasses implement the actual DataFrame transformation."""
