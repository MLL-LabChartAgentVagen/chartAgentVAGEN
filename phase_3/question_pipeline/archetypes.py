"""Archetype definitions — declarative rules for pipeline composition.

An Archetype is a blueprint that defines the *shape* (topology) of a valid
pipeline using abstract NodeSlots.  The PipelineComposer reads an Archetype,
resolves each slot to a concrete PipelineNode, and produces an executable
Pipeline.

NodeSlot is recursive: its ``inputs`` list mirrors PipelineNode.inputs,
allowing representation of sequential chains, parallel forks, and nested
sub-pipelines in a single data structure.

Usage
-----
    from question_pipeline.archetypes import ARCHETYPE_REGISTRY

    archetype = ARCHETYPE_REGISTRY["extrema_focus"]
    # Feed to PipelineComposer.compose(archetype, ...) to instantiate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─── NodeSlot ──────────────────────────────────────────────────────────────────

@dataclass
class NodeSlot:
    """A single positional slot in an archetype tree.

    Each slot constrains which concrete PipelineNode classes can fill it.

    Parameters
    ----------
    allowed_types : list of str
        Node class names that can fill this slot.  Can be exact names
        (e.g. ``"Filter"``) or category tags (e.g. ``"ScalarNode"``).
        The composer resolves these against the NODE_REGISTRY.
    inputs : list of NodeSlot
        Child slots feeding into this slot.
        - Empty list → leaf node (operates on the base view).
        - One item   → unary / sequential chain.
        - Two items  → binary / fork (combinators).
    optional : bool
        If True, this slot may be skipped during random composition.
    param_constraints : dict, optional
        Hard constraints on constructor kwargs for the resolved node.
        Keys are parameter names; values are lists of allowed values.
        During random composition, one value is sampled from each list.
        Example: ``{"ascending": [True, False], "k": [1, 3, 5]}``
    """

    allowed_types: List[str]
    inputs: List["NodeSlot"] = field(default_factory=list)
    optional: bool = False
    param_constraints: Optional[Dict[str, List[Any]]] = None

    # ── Helpers ────────────────────────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        """True if this slot has no child inputs."""
        return len(self.inputs) == 0

    @property
    def is_binary(self) -> bool:
        """True if this slot merges two branches."""
        return len(self.inputs) == 2

    def display(self, indent: int = 0) -> str:
        """Pretty-print the slot tree for debugging."""
        prefix = "  " * indent
        types_str = "|".join(self.allowed_types)
        opt = " (optional)" if self.optional else ""
        constraints = ""
        if self.param_constraints:
            constraints = f"  constraints={self.param_constraints}"
        line = f"{prefix}[{types_str}]{opt}{constraints}"

        lines = [line]
        for child in self.inputs:
            lines.append(child.display(indent + 1))
        return "\n".join(lines)


# ─── Archetype ─────────────────────────────────────────────────────────────────

@dataclass
class Archetype:
    """A named pipeline blueprint with chart compatibility rules.

    Parameters
    ----------
    name : str
        Human-readable identifier (e.g. ``"extrema_focus"``).
    description : str
        Brief explanation of the question pattern this archetype produces.
    compatible_charts : list of str
        Chart types this archetype is valid for.
    structure : NodeSlot
        Root slot of the archetype tree.  The composer walks this
        recursively to build the concrete PipelineNode tree.
    pipeline_type : str
        Label for the resulting Pipeline object
        (``"sequential"``, ``"forked"``, ``"nested"``).
    """

    name: str
    description: str
    compatible_charts: List[str]
    structure: NodeSlot
    pipeline_type: str = "sequential"

    def display(self) -> str:
        """Pretty-print the full archetype for debugging."""
        header = (
            f"Archetype: {self.name} ({self.pipeline_type})\n"
            f"  Charts: {', '.join(self.compatible_charts)}\n"
            f"  Description: {self.description}\n"
            f"  Structure:"
        )
        return f"{header}\n{self.structure.display(indent=2)}"


# ─── Category Expansion Map ───────────────────────────────────────────────────
# Maps category shorthand names → lists of concrete node class names.
# Used by the composer to expand a slot like ["ScalarNode"] into
# ["Max", "Min", "Avg", "Sum", "Count"].

CATEGORY_MAP: Dict[str, List[str]] = {
    "SetNode":       ["Filter", "Sort", "Limit", "GroupBy"],
    "ScalarNode":    ["Max", "Min", "Avg", "Sum", "Count"],
    "ArgNode":       ["ArgMax", "ArgMin"],
    "ReduceNode":    ["Max", "Min", "Avg", "Sum", "Count", "ArgMax", "ArgMin", "ValueAt"],
    "MergeNode":     ["Union", "Intersect", "Difference"],
    "ScalarMerge":   ["Diff", "Ratio"],
}


# ─── Concrete Archetype Definitions ──────────────────────────────────────────

# --------------------------------------------------------------------------- #
# 1. EXTREMA FOCUS                                                            #
#    Shape: [Filter?] → Sort → Limit → [ScalarNode]                           #
#    Question: "What is the {max/avg/sum} {measure} of the top {k}            #
#              {entities} [where {col} {op} {val}]?"                           #
# --------------------------------------------------------------------------- #

EXTREMA_FOCUS = Archetype(
    name="extrema_focus",
    description=(
        "Sort the view, take the top/bottom K entries, then reduce to a "
        "scalar.  Optionally filter first."
    ),
    compatible_charts=[
        "bar_chart", "grouped_bar_chart", "stacked_bar_chart",
        "scatter_plot", "bubble_chart",
    ],
    pipeline_type="sequential",
    structure=NodeSlot(
        allowed_types=["ScalarNode"],       # Root: any scalar reduction
        inputs=[
            NodeSlot(
                allowed_types=["Limit"],
                param_constraints={"k": [1, 3, 5, 10]},
                inputs=[
                    NodeSlot(
                        allowed_types=["Sort"],
                        param_constraints={"ascending": [True, False]},
                        inputs=[
                            NodeSlot(
                                allowed_types=["Filter"],
                                optional=True,        # Filter is optional
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
)


# --------------------------------------------------------------------------- #
# 2. COMPARATIVE FORK                                                         #
#    Shape:  Branch A: Sort(desc) → Limit                                     #
#            Branch B: Sort(asc)  → Limit                                     #
#            Merge:  [MergeNode](A, B) → [ScalarNode]                         #
#    Question: "How many {entities} appear in the top-{a} or bottom-{b}       #
#              by {measure}?"                                                  #
# --------------------------------------------------------------------------- #

COMPARATIVE_FORK = Archetype(
    name="comparative_fork",
    description=(
        "Two parallel branches (e.g. top-K and bottom-K) are merged via "
        "a view combinator, then reduced to a scalar."
    ),
    compatible_charts=[
        "bar_chart", "grouped_bar_chart", "stacked_bar_chart",
        "scatter_plot", "bubble_chart",
    ],
    pipeline_type="forked",
    structure=NodeSlot(
        allowed_types=["ScalarNode"],       # Root: any scalar reduction
        inputs=[
            NodeSlot(
                allowed_types=["MergeNode"],    # Union / Intersect / Difference
                inputs=[
                    # ── Branch A (top-K) ──────────────────────────────
                    NodeSlot(
                        allowed_types=["Limit"],
                        param_constraints={"k": [3, 5]},
                        inputs=[
                            NodeSlot(
                                allowed_types=["Sort"],
                                param_constraints={"ascending": [False]},
                            ),
                        ],
                    ),
                    # ── Branch B (bottom-K) ───────────────────────────
                    NodeSlot(
                        allowed_types=["Limit"],
                        param_constraints={"k": [2, 3]},
                        inputs=[
                            NodeSlot(
                                allowed_types=["Sort"],
                                param_constraints={"ascending": [True]},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
)


# ─── Archetype Registry ──────────────────────────────────────────────────────

ARCHETYPE_REGISTRY: Dict[str, Archetype] = {
    "extrema_focus":    EXTREMA_FOCUS,
    "comparative_fork": COMPARATIVE_FORK,
}


def get_archetypes_for_chart(chart_type: str) -> List[Archetype]:
    """Return all archetypes compatible with *chart_type*."""
    return [
        a for a in ARCHETYPE_REGISTRY.values()
        if chart_type in a.compatible_charts
    ]
