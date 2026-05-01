"""Node registry — central lookup by name, type signature, and chart compatibility."""

from typing import Dict, List, Type

from .base import PipelineNode

from .set_node.filter import Filter
from .set_node.sort import Sort
from .set_node.limit import Limit
from .set_node.group_by import GroupBy

from .scalar_node.max import Max
from .scalar_node.min import Min
from .scalar_node.avg import Avg
from .scalar_node.sum import Sum
from .scalar_node.count import Count
from .scalar_node.arg_max import ArgMax
from .scalar_node.arg_min import ArgMin
from .scalar_node.value_at import ValueAt

from .combinator_node.diff import Diff
from .combinator_node.ratio import Ratio
from .combinator_node.union import Union
from .combinator_node.intersect import Intersect
from .combinator_node.difference import Difference

from .bridge_node.entity_transfer import EntityTransfer
from .bridge_node.value_transfer import ValueTransfer
from .bridge_node.trend_compare import TrendCompare
from .bridge_node.rank_compare import RankCompare


NODE_REGISTRY: Dict[str, Type[PipelineNode]] = {
    # Set nodes (V → V)
    "Filter": Filter,
    "Sort": Sort,
    "Limit": Limit,
    "GroupBy": GroupBy,
    # Scalar nodes (V → S)
    "Max": Max,
    "Min": Min,
    "Avg": Avg,
    "Sum": Sum,
    "Count": Count,
    "ArgMax": ArgMax,
    "ArgMin": ArgMin,
    "ValueAt": ValueAt,
    # Scalar combinators (S,S → S)
    "Diff": Diff,
    "Ratio": Ratio,
    # View combinators (V,V → V)
    "Union": Union,
    "Intersect": Intersect,
    "Difference": Difference,
    # Bridge nodes
    "EntityTransfer": EntityTransfer,
    "ValueTransfer": ValueTransfer,
    "TrendCompare": TrendCompare,
    "RankCompare": RankCompare,
}


def get_compatible_nodes(chart_type: str) -> List[Type[PipelineNode]]:
    """Return all node classes compatible with chart_type."""
    return [cls for cls in NODE_REGISTRY.values() if chart_type in cls.compatible_charts]


def get_nodes_by_signature(input_type: str, output_type: str) -> List[Type[PipelineNode]]:
    """Return node classes matching (input_type → output_type)."""
    return [
        cls for cls in NODE_REGISTRY.values()
        if cls.input_type == input_type and cls.output_type == output_type
    ]
