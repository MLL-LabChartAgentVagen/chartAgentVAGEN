"""SetNode — abstract base for V → V pipeline nodes."""

from abc import abstractmethod
from typing import Any, List, Optional

import pandas as pd

from ..base import PipelineNode, NodeResult


class SetNode(PipelineNode):
    """Abstract base for nodes that transform a view into another view (V → V).

    Subclasses implement _transform(view) → DataFrame.
    _compute() wraps the result in NodeResult("V", ...).
    """

    input_type: str = "V"
    output_type: str = "V"

    def __init__(self, inputs: Optional[List[PipelineNode]] = None):
        super().__init__(inputs=inputs)

    def _compute(self, view: pd.DataFrame) -> NodeResult:
        return NodeResult(result_type="V", value=self._transform(view))

    @abstractmethod
    def _transform(self, view: pd.DataFrame) -> pd.DataFrame:
        """Subclasses implement the actual DataFrame transformation."""
