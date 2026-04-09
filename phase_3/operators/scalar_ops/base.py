"""Base class for scalar operators (V → S)."""

from abc import abstractmethod
from typing import Any

import pandas as pd

from operators.base import Operator, OperatorResult


class ScalarOperator(Operator):
    """Abstract base for operators that reduce a view to a single value.

    Signature: V → S
    """

    input_type: str = "V"
    output_type: str = "S"

    def execute(self, view: pd.DataFrame, **params: Any) -> OperatorResult:
        """Reduce the view and wrap in an OperatorResult(S)."""
        scalar = self._reduce(view, **params)
        return OperatorResult(result_type="S", value=scalar)

    @abstractmethod
    def _reduce(self, view: pd.DataFrame, **params: Any) -> Any:
        """Subclasses implement the actual reduction."""
