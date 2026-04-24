"""Combinator node bases — ScalarCombinatorNode (S,S→S) and ViewCombinatorNode (V,V→V)."""

from abc import abstractmethod
from typing import Any, List, Optional

import pandas as pd

from ..base import PipelineNode, NodeResult


class ScalarCombinatorNode(PipelineNode):
    """Abstract base for nodes that merge two scalars into one ((S,S) → S).

    Subclasses implement _combine(s1, s2) → scalar.
    _compute() wraps the result in NodeResult("S", ...).
    """

    input_type: str = "(S,S)"
    output_type: str = "S"

    def __init__(self, inputs: Optional[List[PipelineNode]] = None):
        super().__init__(inputs=inputs)

    def _compute(self, s1: Any, s2: Any) -> NodeResult:
        return NodeResult(result_type="S", value=self._combine(s1, s2))

    @abstractmethod
    def _combine(self, s1: Any, s2: Any) -> Any:
        """Subclasses implement the actual scalar combination."""


class ViewCombinatorNode(PipelineNode):
    """Abstract base for nodes that merge two views into one ((V,V) → V).

    Subclasses implement _merge(v1, v2) → DataFrame.
    _compute() wraps the result in NodeResult("V", ...).
    """

    input_type: str = "(V,V)"
    output_type: str = "V"

    def __init__(self, inputs: Optional[List[PipelineNode]] = None):
        super().__init__(inputs=inputs)

    def _compute(self, v1: pd.DataFrame, v2: pd.DataFrame) -> NodeResult:
        return NodeResult(result_type="V", value=self._merge(v1, v2))

    @abstractmethod
    def _merge(self, v1: pd.DataFrame, v2: pd.DataFrame) -> pd.DataFrame:
        """Subclasses implement the actual view merge."""
