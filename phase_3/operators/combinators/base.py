"""Base classes for scalar combinators (S, S → S) and view combinators (V, V → V)."""

from abc import abstractmethod
from typing import Any

import pandas as pd

from operators.base import Operator, OperatorResult


class ScalarCombinator(Operator):
    """Abstract base for operators that merge two scalars into one.

    Signature: (S, S) → S
    """

    input_type: str = "(S,S)"
    output_type: str = "S"

    def execute(self, s1: Any, s2: Any, **params: Any) -> OperatorResult:
        """Combine two scalars and wrap in an OperatorResult(S)."""
        result = self._combine(s1, s2, **params)
        return OperatorResult(result_type="S", value=result)

    @abstractmethod
    def _combine(self, s1: Any, s2: Any, **params: Any) -> Any:
        """Subclasses implement the actual scalar combination."""


class ViewCombinator(Operator):
    """Abstract base for operators that merge two views into one.

    Signature: (V, V) → V
    """

    input_type: str = "(V,V)"
    output_type: str = "V"

    def execute(
        self, v1: pd.DataFrame, v2: pd.DataFrame, **params: Any
    ) -> OperatorResult:
        """Merge two views and wrap in an OperatorResult(V)."""
        result_df = self._merge(v1, v2, **params)
        return OperatorResult(result_type="V", value=result_df)

    @abstractmethod
    def _merge(
        self, v1: pd.DataFrame, v2: pd.DataFrame, **params: Any
    ) -> pd.DataFrame:
        """Subclasses implement the actual view merge."""
