"""ScalarNode — abstract base for V → S pipeline nodes."""

from abc import abstractmethod
from typing import Any, List, Optional

import pandas as pd

from ..base import PipelineNode, NodeResult


class ScalarNode(PipelineNode):
    """Abstract base for nodes that reduce a view to a single scalar (V → S).

    Subclasses implement _reduce(view) → scalar value.
    _compute() wraps the result in NodeResult("S", ...).
    """

    input_type: str = "V"
    output_type: str = "S"

    def __init__(self, inputs: Optional[List[PipelineNode]] = None):
        super().__init__(inputs=inputs)

    def _compute(self, view: pd.DataFrame) -> NodeResult:
        return NodeResult(result_type="S", value=self._reduce(view))

    @abstractmethod
    def _reduce(self, view: pd.DataFrame) -> Any:
        """Subclasses implement the actual reduction."""
