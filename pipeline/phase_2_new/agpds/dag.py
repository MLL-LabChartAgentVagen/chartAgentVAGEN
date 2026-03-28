"""
DAG graph algorithms extracted from FactTableSimulator.

This module contains pure graph algorithms that operate on adjacency-list
representations.  They have no dependency on FactTableSimulator instance
state and are fully testable in isolation.

Extracted during the Sprint 6 post-completion refactoring.
Original locations: FactTableSimulator._detect_cycle_in_adjacency,
    FactTableSimulator._topological_sort,
    FactTableSimulator._extract_measure_sub_dag.
"""
from __future__ import annotations

import heapq
import logging
from collections import deque

from agpds.exceptions import CyclicDependencyError

logger = logging.getLogger(__name__)


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
