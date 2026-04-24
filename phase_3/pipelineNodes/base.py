"""PipelineNode — abstract base for all typed pipeline nodes.

Hierarchy:
    PipelineNode (ABC)
    ├── SetNode              — V → V  (transforms a view)
    ├── ScalarNode           — V → S  (reduces a view to a scalar)
    ├── ScalarCombinatorNode — (S, S) → S
    ├── ViewCombinatorNode   — (V, V) → V
    └── BridgeNode           — mixed signatures (cross-chart)

Each concrete node class IS both the tree node (holding child inputs) and the
computation (implementing _compute()).  This replaces the old split between
Operator (computation) and PipelineNode (tree wrapper).

Inputs (child nodes) are passed at construction time; trees are built
bottom-up in pipeline_composer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


# ─── NodeResult ────────────────────────────────────────────────────────────────

@dataclass
class NodeResult:
    """Typed wrapper: holds either a View (DataFrame) or a Scalar."""

    result_type: str  # "V" or "S"
    value: Any        # DataFrame if "V", scalar if "S"

    @property
    def is_view(self) -> bool:
        return self.result_type == "V"

    @property
    def is_scalar(self) -> bool:
        return self.result_type == "S"

    def __repr__(self) -> str:
        if self.is_scalar:
            return f"NodeResult(S={self.value!r})"
        return f"NodeResult(V, {len(self.value)} rows)"


# ─── PipelineNode ──────────────────────────────────────────────────────────────

class PipelineNode(ABC):
    """Abstract base for every node in a pipeline tree.

    Class-level metadata (override in concrete classes):
        name              : short identifier used in display/serialization
        input_type        : "V", "S", "(S,S)", "(V,V)", or "(S,V)"
        output_type       : "V" or "S"
        compatible_charts : chart types this node is valid for
        question_templates: NL question templates (root node)
        subject_templates : NL subject-fragment templates (set nodes)
    """

    name: str = ""
    input_type: str = ""
    output_type: str = ""
    compatible_charts: List[str] = []
    question_templates: List[str] = []
    subject_templates: List[str] = []

    def __init__(self, inputs: Optional[List["PipelineNode"]] = None):
        self.inputs: List["PipelineNode"] = inputs if inputs is not None else []

    # ── Core computation ───────────────────────────────────────────────────

    @abstractmethod
    def _compute(self, *args: Any) -> NodeResult:
        """Subclasses implement the node's actual computation."""

    # ── Tree execution ─────────────────────────────────────────────────────

    def execute(self, view: pd.DataFrame) -> NodeResult:
        """Recursively execute the tree, then apply this node's computation.

        Leaf nodes (no inputs) receive the base view directly.
        Unary nodes receive their single child's result value.
        Binary nodes receive all child result values as positional args.
        """
        if not self.inputs:
            return self._compute(view)

        child_results = [child.execute(view) for child in self.inputs]

        if len(child_results) == 1:
            return self._compute(child_results[0].value)

        values = [r.value for r in child_results]
        return self._compute(*values)

    # ── Rendering ──────────────────────────────────────────────────────────

    def render_subject_fragment(self, **kwargs: Any) -> str:
        """Return a noun-phrase fragment describing the subset this node produces.

        Set nodes (V→V) override this via subject_templates.
        All other node types return empty string by default.
        """
        if not self.subject_templates:
            return ""
        template = self.subject_templates[0]
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def render_subject(self, **context: Any) -> str:
        """Recursively compose a noun-phrase subject from set-node fragments.

        Fragments are accumulated bottom-up (leaf first) and joined with spaces.
        Binary nodes inject branch subjects as branch_a / branch_b.
        """
        if not self.inputs:
            return self.render_subject_fragment(**context)

        if len(self.inputs) == 1:
            child_subject = self.inputs[0].render_subject(**context)
            my_fragment = self.render_subject_fragment(**context)
            parts = [p for p in [child_subject, my_fragment] if p]
            return " ".join(parts)

        branch_subjects = [child.render_subject(**context) for child in self.inputs]
        ctx = {
            **context,
            "branch_a": branch_subjects[0] if branch_subjects else "",
            "branch_b": branch_subjects[1] if len(branch_subjects) > 1 else "",
        }
        return self.render_subject_fragment(**ctx)

    def render_question(self, **context: Any) -> str:
        """Compose a complete question using two-phase rendering.

        Phase 1: collect subject fragments from child set-nodes.
        Phase 2: plug subject into this node's question template.
        """
        if self.inputs:
            if len(self.inputs) == 1:
                subject = self.inputs[0].render_subject(**context)
            else:
                branch_subjects = [child.render_subject(**context) for child in self.inputs]
                subject = self.render_subject_fragment(**{
                    **context,
                    "branch_a": branch_subjects[0] if branch_subjects else "",
                    "branch_b": branch_subjects[1] if len(branch_subjects) > 1 else "",
                })
        else:
            subject = ""

        ctx = {**context, "subject": subject} if subject else context

        for template in self.question_templates:
            try:
                return template.format(**ctx)
            except KeyError:
                continue

        return self.question_templates[0] if self.question_templates else ""

    # ── Display ────────────────────────────────────────────────────────────

    def display(self, indent: int = 0) -> str:
        """Return an indented tree string for debugging."""
        prefix = "  " * indent
        sig = f"{self.input_type} → {self.output_type}"
        lines = [f"{prefix}{self.name} ({sig})"]
        for child in self.inputs:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)

    # ── Properties ─────────────────────────────────────────────────────────

    @property
    def depth(self) -> int:
        if not self.inputs:
            return 1
        return 1 + max(child.depth for child in self.inputs)

    @property
    def op_count(self) -> int:
        return 1 + sum(child.op_count for child in self.inputs)

    # ── Type checking ──────────────────────────────────────────────────────

    def type_check(self) -> bool:
        """Verify that child output types match this node's expected input type."""
        for child in self.inputs:
            if not child.type_check():
                return False

        if not self.inputs:
            return True

        child_output_types = [child.output_type for child in self.inputs]

        if len(child_output_types) == 1:
            return child_output_types[0] == self.input_type

        pair = f"({','.join(child_output_types)})"
        return pair == self.input_type

    def is_compatible(self, chart_type: str) -> bool:
        return chart_type in self.compatible_charts

    # ── Serialization ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "operator": self.name,
            "input_type": self.input_type,
            "output_type": self.output_type,
        }
        if self.inputs:
            d["inputs"] = [child.to_dict() for child in self.inputs]
        return d

    # ── Dunder ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        if not self.inputs:
            return f"{self.__class__.__name__}(leaf)"
        child_reprs = ", ".join(repr(c) for c in self.inputs)
        return f"{self.__class__.__name__}([{child_reprs}])"
