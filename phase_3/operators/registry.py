"""Operator registry — central lookup by name, type signature, and chart compatibility."""

from typing import Dict, List, Type

from operators.base import Operator

from operators.set_ops.filter import Filter
from operators.set_ops.sort import Sort
from operators.set_ops.limit import Limit
from operators.set_ops.group_by import GroupBy

from operators.scalar_ops.max import Max
from operators.scalar_ops.min import Min
from operators.scalar_ops.avg import Avg
from operators.scalar_ops.sum import Sum
from operators.scalar_ops.count import Count
from operators.scalar_ops.arg_max import ArgMax
from operators.scalar_ops.arg_min import ArgMin
from operators.scalar_ops.value_at import ValueAt

from operators.combinators.diff import Diff
from operators.combinators.ratio import Ratio
from operators.combinators.union import Union
from operators.combinators.intersect import Intersect
from operators.combinators.difference import Difference

from operators.bridge_ops.entity_transfer import EntityTransfer
from operators.bridge_ops.value_transfer import ValueTransfer
from operators.bridge_ops.trend_compare import TrendCompare
from operators.bridge_ops.rank_compare import RankCompare


# ── Master registry ───────────────────────────────────────────────────────────
OPERATOR_REGISTRY: Dict[str, Type[Operator]] = {
    # Set operators (V → V)
    "Filter": Filter,
    "Sort": Sort,
    "Limit": Limit,
    "GroupBy": GroupBy,
    # Scalar operators (V → S)
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
    # Bridge operators
    "EntityTransfer": EntityTransfer,
    "ValueTransfer": ValueTransfer,
    "TrendCompare": TrendCompare,
    "RankCompare": RankCompare,
}


# ── Lookup helpers ────────────────────────────────────────────────────────────

def get_compatible_ops(chart_type: str) -> List[Type[Operator]]:
    """Return all operator classes compatible with *chart_type*."""
    return [
        cls for cls in OPERATOR_REGISTRY.values()
        if chart_type in cls.compatible_charts
    ]


def get_ops_by_signature(
    input_type: str, output_type: str
) -> List[Type[Operator]]:
    """Return operator classes matching (*input_type* → *output_type*)."""
    return [
        cls for cls in OPERATOR_REGISTRY.values()
        if cls.input_type == input_type and cls.output_type == output_type
    ]
