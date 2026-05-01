"""Pipeline node hierarchy for typed question-generation pipelines.

Hierarchy:
    PipelineNode (ABC)
    ├── SetNode              — V → V
    ├── ScalarNode           — V → S
    ├── ScalarCombinatorNode — (S, S) → S
    ├── ViewCombinatorNode   — (V, V) → V
    └── BridgeNode           — mixed signatures
"""

from .base import PipelineNode, NodeResult
from .registry import NODE_REGISTRY, get_compatible_nodes, get_nodes_by_signature
