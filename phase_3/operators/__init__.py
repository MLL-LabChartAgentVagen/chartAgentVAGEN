"""Operator algebra for typed question-generation pipelines.

Hierarchy:
    Operator (ABC)
    ├── SetOperator      — V → V
    ├── ScalarOperator   — V → S
    ├── ScalarCombinator — (S, S) → S
    ├── ViewCombinator   — (V, V) → V
    └── BridgeOperator   — mixed signatures
"""

from .base import Operator, OperatorResult
from .registry import OPERATOR_REGISTRY, get_compatible_ops, get_ops_by_signature
