"""Pipeline — typed operator pipeline wrapper.

A Pipeline holds a root PipelineNode (the final node in the chain) plus
view-spec metadata.  Execution, rendering, display, and type-checking all
delegate to the root node.

PipelineNode lives in pipelineNodes/base.py; the Pipeline class here is a
thin wrapper that provides metadata and a unified entry-point.

Example
-------
    from pipelineNodes.set_node import Filter, Sort, Limit
    from pipelineNodes.scalar_node import Avg

    leaf      = Filter("region", "==", "East")
    sort_node = Sort("cost", ascending=False, inputs=[leaf])
    limit_node = Limit(3, inputs=[sort_node])
    root      = Avg("cost", inputs=[limit_node])
    pipe      = Pipeline(root=root, view_specs=[vs])
"""

from __future__ import annotations

import json
import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

_phase3_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _phase3_dir not in sys.path:
    sys.path.insert(0, _phase3_dir)

from pipelineNodes.base import PipelineNode, NodeResult


# ─── Pipeline ─────────────────────────────────────────────────────────────────

@dataclass
class Pipeline:
    """A complete pipeline: root node + metadata.

    The root PipelineNode is the final node in the chain (outermost).
    Execution, rendering, and display all delegate to the root.

    Parameters
    ----------
    root : PipelineNode
        Root of the node tree.
    view_specs : list
        ViewSpec objects this pipeline was built for (metadata context).
    pipeline_type : str
        One of ``"sequential"``, ``"forked"``, ``"nested"``,
        ``"multi_chart"``.
    relationship : str, optional
        Inter-chart relationship type (for multi-chart pipelines).
    """

    root: PipelineNode
    view_specs: List[Any] = field(default_factory=list)
    pipeline_type: str = "sequential"
    relationship: Optional[str] = None

    # ── Delegate to root ──────────────────────────────────────────────────

    def execute(self, view: pd.DataFrame) -> NodeResult:
        """Execute the pipeline on a view DataFrame."""
        return self.root.execute(view)

    def render_question(self, **context: Any) -> str:
        """Compose a full question from node NL templates."""
        return self.root.render_question(**context)

    def display(self) -> str:
        """Return an indented tree string for debugging."""
        header = f"Pipeline({self.pipeline_type}, {self.op_count} ops)"
        return f"{header}\n{self.root.display(indent=1)}"

    def type_check(self) -> bool:
        """Verify all type connections in the pipeline are valid."""
        return self.root.type_check()

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def depth(self) -> int:
        return self.root.depth

    @property
    def op_count(self) -> int:
        return self.root.op_count

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_type": self.pipeline_type,
            "relationship": self.relationship,
            "op_count": self.op_count,
            "depth": self.depth,
            "tree": self.root.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # ── Dunder ────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Pipeline({self.pipeline_type}, "
            f"{self.op_count} ops, depth={self.depth})"
        )
