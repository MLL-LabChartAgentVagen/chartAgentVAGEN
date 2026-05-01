"""PipelineComposer — builds executable Pipelines from Archetype blueprints.

Supports three composition modes:

    EXACT      – The caller provides explicit overrides for every slot.
    RANDOM     – The composer randomly samples valid nodes for each slot.
    ENUMERATE  – The composer returns every legal combination for the archetype.

Usage
-----
    composer = PipelineComposer()

    # Random: one pipeline with random choices
    pipe = composer.compose("extrema_focus", chart_type="bar_chart",
                            measure_col="revenue", mode="RANDOM")

    # Enumerate: all valid pipelines for the archetype
    pipes = composer.compose("extrema_focus", chart_type="bar_chart",
                             measure_col="revenue", mode="ENUMERATE")

    # Exact: caller pins every choice
    pipe = composer.compose("extrema_focus", chart_type="bar_chart",
                            measure_col="revenue", mode="EXACT",
                            overrides={...})
"""

from __future__ import annotations

import itertools
import random
import sys
import os
from typing import Any, Dict, List, Optional, Type

_phase3_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _phase3_dir not in sys.path:
    sys.path.insert(0, _phase3_dir)

from question_pipeline.archetypes import (
    Archetype,
    ARCHETYPE_REGISTRY,
    CATEGORY_MAP,
    NodeSlot,
    get_archetypes_for_chart,
)
from question_pipeline.pipeline import Pipeline
from pipelineNodes.base import PipelineNode
from pipelineNodes.registry import NODE_REGISTRY


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _expand_allowed_types(allowed: List[str]) -> List[str]:
    """Expand category shorthand names into concrete node class names.

    If a name is already a concrete class (present in NODE_REGISTRY), it is
    kept as-is.  If it matches a category in CATEGORY_MAP, it is replaced
    by all concrete names in that category.

    Returns a deduplicated list.
    """
    expanded: List[str] = []
    for name in allowed:
        if name in CATEGORY_MAP:
            expanded.extend(CATEGORY_MAP[name])
        elif name in NODE_REGISTRY:
            expanded.append(name)
        else:
            raise ValueError(
                f"Unknown node type or category: {name!r}.  "
                f"Known nodes: {list(NODE_REGISTRY.keys())}.  "
                f"Known categories: {list(CATEGORY_MAP.keys())}."
            )
    # Deduplicate while preserving order
    seen: set = set()
    result: List[str] = []
    for n in expanded:
        if n not in seen:
            seen.add(n)
            result.append(n)
    return result


def _filter_by_chart(node_names: List[str], chart_type: str) -> List[str]:
    """Keep only node classes compatible with *chart_type*.

    Nodes with an empty ``compatible_charts`` list (e.g. combinators)
    are always included — they are chart-agnostic by design.
    """
    result: List[str] = []
    for name in node_names:
        cls = NODE_REGISTRY[name]
        if not cls.compatible_charts or chart_type in cls.compatible_charts:
            result.append(name)
    return result


# ─── PipelineComposer ────────────────────────────────────────────────────────

class PipelineComposer:
    """Factory that builds Pipeline objects from Archetype blueprints.

    The composer walks the recursive NodeSlot tree of an Archetype,
    resolves each slot to a concrete PipelineNode class, instantiates
    nodes with the appropriate parameters, and wraps the result in a
    Pipeline that passes type_check().
    """

    # ── Public API ────────────────────────────────────────────────────────

    def compose(
        self,
        archetype_name: str,
        *,
        chart_type: str,
        measure_col: str,
        view_spec: Any = None,
        mode: str = "RANDOM",
        overrides: Optional[Dict[str, Any]] = None,
        skip_probability: float = 0.5,
    ) -> List[Pipeline]:
        """Build one or more Pipelines from the named archetype.

        Parameters
        ----------
        archetype_name : str
            Key into ARCHETYPE_REGISTRY.
        chart_type : str
            The target chart type (used to filter compatible nodes).
        measure_col : str
            Column name to use for Sort, Avg, Max, etc.
        view_spec : Any, optional
            ViewSpec to attach to the resulting Pipeline(s).
        mode : str
            ``"RANDOM"`` — one pipeline with random choices.
            ``"ENUMERATE"`` — all valid pipelines for the archetype.
            ``"EXACT"`` — use *overrides* to pin every choice.
        overrides : dict, optional
            For EXACT mode.  Maps dot-separated slot paths to
            ``{"node": "Avg", "params": {"column": "revenue"}}``.
        skip_probability : float
            Probability of skipping an optional slot in RANDOM mode.

        Returns
        -------
        list of Pipeline
            A single-element list for RANDOM/EXACT; potentially many
            for ENUMERATE.
        """
        if archetype_name not in ARCHETYPE_REGISTRY:
            raise ValueError(
                f"Unknown archetype: {archetype_name!r}.  "
                f"Available: {list(ARCHETYPE_REGISTRY.keys())}"
            )

        archetype = ARCHETYPE_REGISTRY[archetype_name]

        if chart_type not in archetype.compatible_charts:
            raise ValueError(
                f"Archetype {archetype_name!r} is not compatible with "
                f"chart_type={chart_type!r}.  Allowed: "
                f"{archetype.compatible_charts}"
            )

        view_specs = [view_spec] if view_spec else []

        if mode == "RANDOM":
            root = self._build_random(
                archetype.structure,
                chart_type=chart_type,
                measure_col=measure_col,
                skip_prob=skip_probability,
            )
            if root is None:
                raise RuntimeError(
                    f"Failed to build pipeline: all nodes were skipped "
                    f"for archetype {archetype_name!r}."
                )
            pipe = Pipeline(
                root=root,
                view_specs=view_specs,
                pipeline_type=archetype.pipeline_type,
            )
            assert pipe.type_check(), (
                f"Pipeline from archetype {archetype_name!r} failed "
                f"type_check:\n{pipe.display()}"
            )
            return [pipe]

        elif mode == "ENUMERATE":
            all_trees = self._enumerate(
                archetype.structure,
                chart_type=chart_type,
                measure_col=measure_col,
            )
            pipelines = []
            for root in all_trees:
                pipe = Pipeline(
                    root=root,
                    view_specs=view_specs,
                    pipeline_type=archetype.pipeline_type,
                )
                if pipe.type_check():
                    pipelines.append(pipe)
            return pipelines

        elif mode == "EXACT":
            if not overrides:
                raise ValueError("EXACT mode requires 'overrides' dict.")
            root = self._build_exact(
                archetype.structure,
                chart_type=chart_type,
                measure_col=measure_col,
                overrides=overrides,
                path="root",
            )
            pipe = Pipeline(
                root=root,
                view_specs=view_specs,
                pipeline_type=archetype.pipeline_type,
            )
            assert pipe.type_check(), (
                f"EXACT pipeline from archetype {archetype_name!r} failed "
                f"type_check:\n{pipe.display()}"
            )
            return [pipe]

        else:
            raise ValueError(
                f"Unknown mode: {mode!r}.  Must be RANDOM, ENUMERATE, or EXACT."
            )

    # ── RANDOM mode ───────────────────────────────────────────────────────

    def _build_random(
        self,
        slot: NodeSlot,
        *,
        chart_type: str,
        measure_col: str,
        skip_prob: float,
    ) -> Optional[PipelineNode]:
        """Recursively walk the slot tree and build a random pipeline."""

        # Handle optional slots
        if slot.optional and random.random() < skip_prob:
            return None

        # Resolve which concrete node classes can fill this slot
        expanded = _expand_allowed_types(slot.allowed_types)
        compatible = _filter_by_chart(expanded, chart_type)
        if not compatible:
            if slot.optional:
                return None
            raise RuntimeError(
                f"No compatible nodes for slot {slot.allowed_types} "
                f"with chart_type={chart_type!r}."
            )

        # Pick one at random
        chosen_name = random.choice(compatible)

        # Recursively build child nodes
        child_nodes: List[PipelineNode] = []
        for child_slot in slot.inputs:
            child = self._build_random(
                child_slot,
                chart_type=chart_type,
                measure_col=measure_col,
                skip_prob=skip_prob,
            )
            if child is not None:
                child_nodes.append(child)

        # Instantiate the chosen node
        node = self._instantiate_node(
            chosen_name,
            inputs=child_nodes,
            measure_col=measure_col,
            param_constraints=slot.param_constraints,
        )
        return node

    # ── ENUMERATE mode ────────────────────────────────────────────────────

    def _enumerate(
        self,
        slot: NodeSlot,
        *,
        chart_type: str,
        measure_col: str,
    ) -> List[PipelineNode]:
        """Return all valid concrete trees for this slot subtree.

        At each slot, we take the cartesian product of:
            - all compatible node choices for this slot
            - all child tree combinations (recursively)

        Optional slots produce two branches: included and skipped.
        """
        # Resolve concrete node names
        expanded = _expand_allowed_types(slot.allowed_types)
        compatible = _filter_by_chart(expanded, chart_type)

        if not compatible:
            return []

        # Enumerate child combinations
        if slot.inputs:
            child_combos_per_slot: List[List[Optional[List[PipelineNode]]]] = []
            for child_slot in slot.inputs:
                child_trees = self._enumerate(
                    child_slot,
                    chart_type=chart_type,
                    measure_col=measure_col,
                )
                options: List[Optional[List[PipelineNode]]] = []
                # Each child_tree is a single PipelineNode (a complete subtree)
                for ct in child_trees:
                    options.append([ct])

                if child_slot.optional:
                    options.append(None)  # Represent "skipped"

                if not options:
                    # No valid children and not optional — this slot is invalid
                    return []

                child_combos_per_slot.append(options)

            # Cartesian product across all child slots
            all_child_combos = list(itertools.product(*child_combos_per_slot))
        else:
            # Leaf node — no children
            all_child_combos = [()]

        # For each node choice × each child combination, build a tree
        results: List[PipelineNode] = []
        for chosen_name in compatible:
            for combo in all_child_combos:
                # Flatten child nodes, skipping None (optional slots)
                child_nodes: List[PipelineNode] = []
                for item in combo:
                    if item is not None:
                        child_nodes.extend(item)

                # Enumerate parameter variations
                param_combos = self._enumerate_params(slot.param_constraints)
                for params in param_combos:
                    node = self._instantiate_node(
                        chosen_name,
                        inputs=child_nodes.copy(),
                        measure_col=measure_col,
                        param_constraints=None,
                        exact_params=params,
                    )
                    results.append(node)

        return results

    def _enumerate_params(
        self, constraints: Optional[Dict[str, List[Any]]]
    ) -> List[Dict[str, Any]]:
        """Expand param_constraints into all combinations.

        Example: {"k": [3, 5], "ascending": [True, False]}
        → [{"k": 3, "ascending": True}, {"k": 3, "ascending": False},
           {"k": 5, "ascending": True}, {"k": 5, "ascending": False}]
        """
        if not constraints:
            return [{}]

        keys = list(constraints.keys())
        value_lists = [constraints[k] for k in keys]
        combos = list(itertools.product(*value_lists))
        return [dict(zip(keys, vals)) for vals in combos]

    # ── EXACT mode ────────────────────────────────────────────────────────

    def _build_exact(
        self,
        slot: NodeSlot,
        *,
        chart_type: str,
        measure_col: str,
        overrides: Dict[str, Any],
        path: str,
    ) -> PipelineNode:
        """Build a pipeline using caller-specified overrides at each slot.

        *overrides* maps dot-separated paths to dicts like:
            {"node": "Avg", "params": {"column": "revenue"}}

        Path format: "root", "root.0", "root.0.0", "root.0.1", etc.
        """
        override = overrides.get(path, {})
        chosen_name = override.get("node")
        exact_params = override.get("params", {})

        if not chosen_name:
            # Fall back to first allowed type
            expanded = _expand_allowed_types(slot.allowed_types)
            compatible = _filter_by_chart(expanded, chart_type)
            if not compatible:
                raise RuntimeError(
                    f"No compatible nodes at path {path!r} for "
                    f"chart_type={chart_type!r}."
                )
            chosen_name = compatible[0]

        # Recurse into children
        child_nodes: List[PipelineNode] = []
        for i, child_slot in enumerate(slot.inputs):
            child_path = f"{path}.{i}"
            child = self._build_exact(
                child_slot,
                chart_type=chart_type,
                measure_col=measure_col,
                overrides=overrides,
                path=child_path,
            )
            child_nodes.append(child)

        return self._instantiate_node(
            chosen_name,
            inputs=child_nodes,
            measure_col=measure_col,
            param_constraints=slot.param_constraints,
            exact_params=exact_params,
        )

    # ── Node Instantiation ────────────────────────────────────────────────

    def _instantiate_node(
        self,
        node_name: str,
        *,
        inputs: List[PipelineNode],
        measure_col: str,
        param_constraints: Optional[Dict[str, List[Any]]] = None,
        exact_params: Optional[Dict[str, Any]] = None,
    ) -> PipelineNode:
        """Create a concrete PipelineNode instance from its class name.

        Resolves constructor parameters using (in priority order):
            1. exact_params (from EXACT mode or enumeration)
            2. Random sample from param_constraints
            3. Default inference from measure_col

        Parameters
        ----------
        node_name : str
            Key into NODE_REGISTRY.
        inputs : list of PipelineNode
            Already-built child nodes to attach.
        measure_col : str
            Default column name for measure-based nodes.
        param_constraints : dict, optional
            Slot-level constraints to sample from (RANDOM mode).
        exact_params : dict, optional
            Explicit parameters (EXACT mode / ENUMERATE mode).
        """
        cls = NODE_REGISTRY[node_name]

        # Build the kwargs for this node's constructor
        kwargs: Dict[str, Any] = {}

        # Merge constraints (randomly sampled) with exact overrides
        if param_constraints and not exact_params:
            for key, values in param_constraints.items():
                kwargs[key] = random.choice(values)

        if exact_params:
            kwargs.update(exact_params)

        # Infer standard parameters from measure_col if not already set
        if node_name in ("Sort",):
            kwargs.setdefault("column", measure_col)

        if node_name in ("Max", "Min", "Avg", "Sum"):
            kwargs.setdefault("column", measure_col)

        if node_name in ("ArgMax", "ArgMin"):
            kwargs.setdefault("column", measure_col)

        if node_name in ("ValueAt",):
            kwargs.setdefault("column", measure_col)

        # Limit just needs k
        if node_name == "Limit":
            kwargs.setdefault("k", 3)

        # Count has no special params
        # Union, Intersect, Difference have no special params

        # Attach inputs
        kwargs["inputs"] = inputs if inputs else None

        return cls(**kwargs)


# ─── Convenience ──────────────────────────────────────────────────────────────

def list_archetypes() -> None:
    """Print all registered archetypes and their slot trees."""
    for name, archetype in ARCHETYPE_REGISTRY.items():
        print(archetype.display())
        print()
