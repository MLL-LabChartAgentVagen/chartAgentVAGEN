"""
SDK DAG construction and graph algorithms.

This module combines:
  - Pure graph algorithms (cycle detection, topological sort, sub-DAG extraction)
    formerly in phase_2/dag.py
  - Full-DAG assembly logic formerly in FactTableSimulator._build_full_dag()
    and related helpers

All functions are stateless — they accept explicit parameters rather than
reading from `self`. The FactTableSimulator delegates to these functions
via thin forwarding methods.

Implements: §2.3, §2.4 (unified full-column DAG)
"""
from __future__ import annotations

import heapq
import logging
from collections import deque
from typing import Any

from ..exceptions import CyclicDependencyError
from ..types import DimensionGroup, GroupDependency

logger = logging.getLogger(__name__)


# =====================================================================
# Pure Graph Algorithms (from phase_2/dag.py)
# =====================================================================

def detect_cycle_in_adjacency(
    adjacency: dict[str, list[str]],
) -> list[str] | None:
    """Find a cycle in a directed graph represented as an adjacency list.

    [Subtask 1.5.5, 1.7.3 helper]

    Uses Kahn's algorithm (BFS topological sort).  If not all nodes are
    visited, a cycle exists; DFS is then used to extract the cycle path.

    Args:
        adjacency: Forward adjacency dict {node: [successors]}.

    Returns:
        None if acyclic; otherwise a list of node names forming the
        cycle (first and last elements are the same node).
    """
    all_nodes: set[str] = set(adjacency.keys())
    for successors in adjacency.values():
        all_nodes.update(successors)

    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    for node, successors in adjacency.items():
        for succ in successors:
            in_degree[succ] += 1

    queue: deque[str] = deque(
        n for n, deg in in_degree.items() if deg == 0
    )
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1
        for succ in adjacency.get(node, []):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    if visited_count == len(all_nodes):
        return None

    cycle_nodes = {n for n, deg in in_degree.items() if deg > 0}
    visited: set[str] = set()
    path: list[str] = []

    def _dfs_find_cycle(node: str) -> list[str] | None:
        visited.add(node)
        path.append(node)
        for succ in adjacency.get(node, []):
            if succ not in cycle_nodes:
                continue
            if succ in path:
                cycle_start = path.index(succ)
                return path[cycle_start:] + [succ]
            if succ not in visited:
                result = _dfs_find_cycle(succ)
                if result is not None:
                    return result
        path.pop()
        return None

    start = next(iter(cycle_nodes))
    cycle_path = _dfs_find_cycle(start)

    if cycle_path is None:
        first = next(iter(cycle_nodes))
        cycle_path = [first, "...", first]

    return cycle_path


def topological_sort(
    adjacency: dict[str, list[str]],
) -> list[str]:
    """Compute a deterministic topological ordering with lexicographic
    tie-breaking.

    [Subtask 3.1.2]

    Uses Kahn's algorithm with a min-heap so that when multiple nodes have
    zero in-degree, the lexicographically smallest name is chosen first.

    Args:
        adjacency: Forward adjacency dict {node: [successors]}.

    Returns:
        List of node names in a valid topological order.

    Raises:
        CyclicDependencyError: If the graph contains a cycle.
    """
    all_nodes: set[str] = set(adjacency.keys())
    for successors in adjacency.values():
        all_nodes.update(successors)

    in_degree: dict[str, int] = {n: 0 for n in all_nodes}
    for node, successors in adjacency.items():
        for succ in successors:
            in_degree[succ] += 1

    heap: list[str] = [n for n, deg in in_degree.items() if deg == 0]
    heapq.heapify(heap)

    result: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for succ in adjacency.get(node, []):
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                heapq.heappush(heap, succ)

    if len(result) != len(all_nodes):
        cycle_path = detect_cycle_in_adjacency(adjacency)
        if cycle_path is not None:
            raise CyclicDependencyError(cycle_path)
        remaining = all_nodes - set(result)
        first = sorted(remaining)[0]
        raise CyclicDependencyError([first, "...", first])

    logger.debug("topological_sort: order = %s", result)
    return result


def extract_measure_sub_dag(
    full_dag: dict[str, list[str]],
    measure_names: set[str],
) -> tuple[dict[str, list[str]], list[str]]:
    """Extract the measure-only sub-DAG and its topological order.

    [Subtask 3.2.1]

    Filters *full_dag* to retain only nodes in *measure_names* and edges
    connecting measures to measures, then produces a topological order.

    Args:
        full_dag: Full generation DAG adjacency dict.
        measure_names: Set of column names whose type is ``"measure"``.

    Returns:
        Tuple of (measure_adjacency, measure_topo_order).
    """
    measure_adj: dict[str, list[str]] = {m: [] for m in measure_names}
    for m_name in measure_names:
        for succ in full_dag.get(m_name, []):
            if succ in measure_names:
                measure_adj[m_name].append(succ)

    measure_order = topological_sort(measure_adj)

    logger.debug(
        "extract_measure_sub_dag: %d measures, order = %s",
        len(measure_order),
        measure_order,
    )

    return measure_adj, measure_order


# =====================================================================
# Full-DAG Assembly (from simulator.py _build_full_dag)
# =====================================================================

def build_full_dag(
    columns: dict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    measure_dag: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Build the full generation DAG from all registered declarations.

    [Subtask 3.1.1]

    Assembles edges from four sources:
      1. Within-group hierarchy (parent -> child)
      2. Cross-group root dependencies (on[0] -> child_root)
      3. Temporal derivation (root -> derived features)
      4. Measure predictor references (effect predictor -> measure)
      5. Measure-measure DAG edges (upstream -> downstream)

    Args:
        columns: Column registry (name -> metadata dict).
        groups: Group registry (name -> DimensionGroup).
        group_dependencies: Cross-group dependency list.
        measure_dag: Pre-computed measure DAG edges.

    Returns:
        Forward adjacency dict for the unified generation DAG.

    Raises:
        CyclicDependencyError: If the assembled DAG contains a cycle.
    """
    # Initialize adjacency with all known column names as nodes
    adjacency: dict[str, list[str]] = {col: [] for col in columns}

    # ===== Edge Type 1: Within-group hierarchy =====
    for col_name, col_meta in columns.items():
        parent = col_meta.get("parent")
        if parent is not None and parent in adjacency:
            adjacency[parent].append(col_name)

    # ===== Edge Type 2: Cross-group root dependencies =====
    for dep in group_dependencies:
        for parent_root in dep.on:
            if parent_root in adjacency:
                adjacency[parent_root].append(dep.child_root)

    # ===== Edge Type 3: Temporal derivation =====
    for col_name, col_meta in columns.items():
        if col_meta.get("type") == "temporal_derived":
            source = col_meta.get("source")
            if source is not None and source in adjacency:
                adjacency[source].append(col_name)

    # ===== Edge Type 4: Measure predictor references =====
    for col_name, col_meta in columns.items():
        if col_meta.get("type") != "measure":
            continue

        measure_type = col_meta.get("measure_type")

        if measure_type == "stochastic":
            predictor_cols = collect_stochastic_predictor_cols(
                col_meta.get("param_model", {}), columns
            )
            for pred_col in predictor_cols:
                if pred_col in adjacency:
                    adjacency[pred_col].append(col_name)

        elif measure_type == "structural":
            effects = col_meta.get("effects", {})
            predictor_cols = collect_structural_predictor_cols(
                effects, columns
            )
            for pred_col in predictor_cols:
                if pred_col in adjacency:
                    adjacency[pred_col].append(col_name)

    # ===== Edge Type 5: Measure-measure DAG edges =====
    for upstream, downstreams in measure_dag.items():
        for downstream in downstreams:
            if upstream in adjacency:
                adjacency[upstream].append(downstream)

    # ===== Deduplicate edges =====
    for node in adjacency:
        adjacency[node] = list(dict.fromkeys(adjacency[node]))

    # ===== Defense-in-depth cycle check =====
    cycle_path = detect_cycle_in_adjacency(adjacency)
    if cycle_path is not None:
        raise CyclicDependencyError(cycle_path)

    logger.debug(
        "build_full_dag: %d nodes, %d edges.",
        len(adjacency),
        sum(len(succs) for succs in adjacency.values()),
    )

    return adjacency


# =====================================================================
# DAG Edge Collection Helpers (from simulator.py)
# =====================================================================

def collect_stochastic_predictor_cols(
    param_model: dict[str, Any],
    columns: dict[str, dict[str, Any]],
) -> set[str]:
    """Extract categorical predictor column names from a stochastic
    measure's param_model.

    [Subtask 3.1.1 helper]

    Scans each parameter value in param_model. If the value is a dict
    with an "effects" key, the keys of the effects sub-dict are
    categorical column names that act as predictors for this measure.

    Args:
        param_model: The param_model dict from a stochastic measure's
                     column metadata.
        columns: Column registry for existence checks.

    Returns:
        Set of categorical column names referenced as predictors.
    """
    predictor_cols: set[str] = set()

    for _param_key, value in param_model.items():
        if not isinstance(value, dict):
            continue
        effects = value.get("effects")
        if not isinstance(effects, dict):
            continue

        for col_name in effects:
            if col_name in columns:
                predictor_cols.add(col_name)

    return predictor_cols


def collect_structural_predictor_cols(
    effects: dict[str, dict[str, float]],
    columns: dict[str, dict[str, Any]],
) -> set[str]:
    """Resolve structural measure effects to their categorical predictor
    columns.

    [Subtask 3.1.1 helper]

    For each effect name in a structural measure's effects dict, finds
    the categorical column whose declared value set matches the inner
    dict's key set.

    Args:
        effects: The effects dict from a structural measure's column
                 metadata.
        columns: Column registry for value set matching.

    Returns:
        Set of categorical column names that act as predictors.
    """
    predictor_cols: set[str] = set()

    for _effect_name, val_map in effects.items():
        if not isinstance(val_map, dict) or len(val_map) == 0:
            continue

        inner_keys = set(val_map.keys())
        for col_name, col_meta in columns.items():
            if col_meta.get("type") != "categorical":
                continue
            if set(col_meta["values"]) == inner_keys:
                predictor_cols.add(col_name)
                break

    return predictor_cols


# =====================================================================
# Cycle-Check Helpers (from simulator.py)
# =====================================================================

def check_measure_dag_acyclic(
    measure_dag: dict[str, list[str]],
    new_node: str,
    depends_on: list[str],
) -> None:
    """Verify adding edges to the measure DAG would not create a cycle.

    [Subtask 1.5.5]

    Builds a tentative adjacency list including the proposed new node
    and edges, then runs cycle detection. Raises CyclicDependencyError
    if a cycle would be created.

    Args:
        measure_dag: Current measure DAG adjacency dict.
        new_node: Name of the new measure being declared.
        depends_on: List of upstream measure names.

    Raises:
        CyclicDependencyError: If a cycle would be created.
    """
    tentative: dict[str, list[str]] = {
        k: list(v) for k, v in measure_dag.items()
    }
    tentative.setdefault(new_node, [])
    for dep in depends_on:
        tentative.setdefault(dep, [])
        tentative[dep].append(new_node)

    cycle_path = detect_cycle_in_adjacency(tentative)
    if cycle_path is not None:
        raise CyclicDependencyError(cycle_path)


def check_root_dag_acyclic(
    group_dependencies: list[GroupDependency],
    new_child: str,
    new_parent: str,
) -> None:
    """Verify adding a root-level dependency edge preserves DAG property.

    [Subtask 1.7.3]

    Builds the complete root-level dependency adjacency list from
    existing group_dependencies plus the proposed new edge, then
    runs cycle detection. Raises CyclicDependencyError if a cycle
    would be created.

    Args:
        group_dependencies: Current group dependency list.
        new_child: The dependent root column.
        new_parent: The conditioning root column.

    Raises:
        CyclicDependencyError: If a cycle would be created.
    """
    adjacency: dict[str, list[str]] = {}
    for dep in group_dependencies:
        for parent in dep.on:
            adjacency.setdefault(parent, [])
            adjacency.setdefault(dep.child_root, [])
            adjacency[parent].append(dep.child_root)

    adjacency.setdefault(new_parent, [])
    adjacency.setdefault(new_child, [])
    adjacency[new_parent].append(new_child)

    cycle_path = detect_cycle_in_adjacency(adjacency)
    if cycle_path is not None:
        exc = CyclicDependencyError(cycle_path)
        arrow_chain = " → ".join(f"'{n}'" for n in cycle_path)
        exc.message = f"Root dependency {arrow_chain} forms a cycle."
        raise exc
