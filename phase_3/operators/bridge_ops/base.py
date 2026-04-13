"""Base class for bridge operators (cross-chart connections)."""

from abc import abstractmethod
from typing import Any

import pandas as pd

from operators.base import Operator, OperatorResult


class BridgeOperator(Operator):
    """Abstract base for operators that connect two charts.

    Bridge operators have mixed signatures:
    - EntityTransfer, ValueTransfer: (S, V) → V
    - TrendCompare, RankCompare:     (V, V) → S

    Subclasses set their own input_type and output_type.
    """

    @abstractmethod
    def execute(self, *inputs: Any) -> OperatorResult:
        """Bridge-specific execution — subclasses define the exact signature."""
