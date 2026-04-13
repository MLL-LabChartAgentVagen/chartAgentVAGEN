"""PipelineNode and Pipeline — typed operator chains for QA generation.

A PipelineNode is a single node in an operator tree.  Each node holds an
operator and a list of input nodes:

    []      → leaf node, operates on the base view
    [n]     → unary, sequential chain (linked list)
    [a, b]  → binary, fork/combinator (tree)

A Pipeline is a thin wrapper that holds the root node plus view-spec
metadata for logging and display.

Examples
--------
Sequential (V → Filter → Sort → Avg → S)::

    n1 = PipelineNode(Filter("region", "==", "East"), inputs=[])
    n2 = PipelineNode(Sort("cost", ascending=False),  inputs=[n1])
    root = PipelineNode(Avg("cost"),                   inputs=[n2])
    pipe = Pipeline(root=root, view_specs=[vs])

Forked (Union of two branches → Avg)::

    a = PipelineNode(Limit(3), inputs=[PipelineNode(Sort("cost"), inputs=[])])
    b = PipelineNode(Limit(2), inputs=[PipelineNode(Sort("cost", True), inputs=[])])
    merged = PipelineNode(Union(), inputs=[a, b])
    root = PipelineNode(Avg("cost"), inputs=[merged])
    pipe = Pipeline(root=root, view_specs=[vs])
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

import sys, os
_phase3_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _phase3_dir not in sys.path:
    sys.path.insert(0, _phase3_dir)

from operators.base import Operator, OperatorResult


# ─── PipelineNode ─────────────────────────────────────────────────────────────

@dataclass
class PipelineNode:
    """A single node in an operator tree.

    Parameters
    ----------
    operator : Operator
        The operator this node applies.
    inputs : list of PipelineNode
        Child nodes whose results feed into this operator.
        Empty list means this is a leaf node (operates on base view).
    """

    operator: Operator
    inputs: List["PipelineNode"] = field(default_factory=list)

    # ── Execution ─────────────────────────────────────────────────────────

    def execute(self, view: pd.DataFrame) -> OperatorResult:
        """Recursively execute the operator tree.

        Leaf nodes apply their operator directly to the base view.
        Inner nodes first execute their children, then pass child results
        as arguments to this node's operator.

        Parameters
        ----------
        view : DataFrame
            The base view data.  Leaf nodes operate on this directly.

        Returns
        -------
        OperatorResult
            The typed result (V or S) of this node's operator.
        """
        if not self.inputs:
            # Leaf — apply operator directly to the base view
            return self.operator.execute(view)

        # Recurse into children
        child_results = [child.execute(view) for child in self.inputs]

        if len(child_results) == 1:
            # Unary — single child feeds value to this operator
            return self.operator.execute(child_results[0].value)
        else:
            # Binary (or n-ary) — pass all child values as positional args
            values = [r.value for r in child_results]
            return self.operator.execute(*values)

    # ── Question Rendering ────────────────────────────────────────────────

    def render_question(self, **context: Any) -> str:
        """Recursively compose question fragments from the operator tree.

        Each operator contributes its NL fragment via
        ``operator.render_question()``.  Children are rendered first
        (inside-out), and their fragments are joined with the parent
        fragment to form a complete question.

        Parameters
        ----------
        **context : Any
            Extra context (column names, entity names) for template
            filling.

        Returns
        -------
        str
            Composed question fragment.
        """
        if not self.inputs:
            return self.operator.render_question(**context)

        # Render children first (inside-out)
        child_fragments = [
            child.render_question(**context) for child in self.inputs
        ]

        parent_fragment = self.operator.render_question(**context)

        # Join non-empty fragments
        parts = [f for f in child_fragments + [parent_fragment] if f]
        return " ".join(parts)

    # ── Display ───────────────────────────────────────────────────────────

    def display(self, indent: int = 0) -> str:
        """Recursively build an indented tree string for debugging.

        Example output::

            Avg (V → S)
              Sort (V → V)
                Filter (V → V)

        Parameters
        ----------
        indent : int
            Current indentation level.

        Returns
        -------
        str
            Multi-line indented representation of the operator tree.
        """
        prefix = "  " * indent
        sig = f"{self.operator.input_type} → {self.operator.output_type}"
        line = f"{prefix}{self.operator.name} ({sig})"

        lines = [line]
        for child in self.inputs:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def depth(self) -> int:
        """Maximum depth of the tree rooted at this node."""
        if not self.inputs:
            return 1
        return 1 + max(child.depth for child in self.inputs)

    @property
    def op_count(self) -> int:
        """Total number of operators in the tree."""
        return 1 + sum(child.op_count for child in self.inputs)

    # ── Type Checking ─────────────────────────────────────────────────────

    def type_check(self) -> bool:
        """Verify that child output types match this operator's input type.

        Recursively checks the entire tree.  Returns True if every
        connection is type-compatible.
        """
        # Check children first (recursive)
        for child in self.inputs:
            if not child.type_check():
                return False

        if not self.inputs:
            # Leaf — no children to check against
            return True

        child_output_types = [
            child.operator.output_type for child in self.inputs
        ]

        if len(child_output_types) == 1:
            # Unary: child output must match this operator's input type
            return child_output_types[0] == self.operator.input_type

        # Binary: check against expected pair, e.g. "(V,V)" or "(S,S)"
        pair = f"({','.join(child_output_types)})"
        return pair == self.operator.input_type

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-safe dict (no DataFrames)."""
        d: Dict[str, Any] = {
            "operator": self.operator.name,
            "input_type": self.operator.input_type,
            "output_type": self.operator.output_type,
        }
        if self.inputs:
            d["inputs"] = [child.to_dict() for child in self.inputs]
        return d

    # ── Dunder ────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        if not self.inputs:
            return f"PipelineNode({self.operator.name}, leaf)"
        child_reprs = ", ".join(repr(c) for c in self.inputs)
        return f"PipelineNode({self.operator.name}, [{child_reprs}])"


# ─── Pipeline ─────────────────────────────────────────────────────────────────

@dataclass
class Pipeline:
    """A complete operator pipeline: root node + metadata.

    The root PipelineNode is the final operator in the chain (outermost).
    Execution, rendering, and display all delegate to the root.

    Parameters
    ----------
    root : PipelineNode
        Root of the operator tree.
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

    def execute(self, view: pd.DataFrame) -> OperatorResult:
        """Execute the pipeline on a view DataFrame."""
        return self.root.execute(view)

    def render_question(self, **context: Any) -> str:
        """Compose a full question from operator NL fragments."""
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
        """Maximum depth of the operator tree."""
        return self.root.depth

    @property
    def op_count(self) -> int:
        """Total number of operators."""
        return self.root.op_count

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "pipeline_type": self.pipeline_type,
            "relationship": self.relationship,
            "op_count": self.op_count,
            "depth": self.depth,
            "tree": self.root.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # ── Dunder ────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Pipeline({self.pipeline_type}, "
            f"{self.op_count} ops, depth={self.depth})"
        )
