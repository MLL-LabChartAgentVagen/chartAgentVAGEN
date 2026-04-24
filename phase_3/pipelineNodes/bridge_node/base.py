"""BridgeNode — abstract base for cross-chart pipeline nodes."""

from abc import abstractmethod
from typing import Any, List, Optional

from ..base import PipelineNode, NodeResult


class BridgeNode(PipelineNode):
    """Abstract base for nodes that connect two charts (mixed signatures).

    Bridge nodes have varied signatures:
        EntityTransfer, ValueTransfer : (S, V) → V
        TrendCompare, RankCompare     : (V, V) → S

    Subclasses set their own input_type / output_type and implement _compute().
    """

    def __init__(self, inputs: Optional[List[PipelineNode]] = None):
        super().__init__(inputs=inputs)

    @abstractmethod
    def _compute(self, *args: Any) -> NodeResult:
        """Bridge-specific computation — subclasses define the exact signature."""
