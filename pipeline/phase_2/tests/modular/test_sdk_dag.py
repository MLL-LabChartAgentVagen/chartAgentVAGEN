"""
Tests for SDK DAG operations (pure input-output validation).

Tested functions:
- topological_sort
- build_full_dag
- detect_cycle_in_adjacency
"""
from __future__ import annotations

import pytest

from pipeline.phase_2.exceptions import CyclicDependencyError
from pipeline.phase_2.sdk.dag import topological_sort, build_full_dag, detect_cycle_in_adjacency
from pipeline.phase_2.types import DimensionGroup, GroupDependency


class TestTopologicalSort:
    """Tests for Kahn's algorithm implementation."""

    def test_linear_graph(self):
        """A simple A -> B -> C graph."""
        adjacency = {"a": ["b"], "b": ["c"], "c": []}
        result = topological_sort(adjacency)
        # B must come before A, C must come before B, etc.
        # Wait, the topological_sort algorithm processes dependencies.
        # If A depends on B, B must be processed first.
        # Let's check what adjacency means in our DAG. It's usually adj[node] = [dependencies].
        # In `topological_sort` docstring: adj[node] = [deps].
        # So "a": ["b"] means "a" depends on "b". Therefore "b" before "a".
        assert result.index("a") < result.index("b")
        assert result.index("b") < result.index("c")

    def test_independent_nodes(self):
        """Nodes with no dependencies."""
        adjacency = {"a": [], "b": [], "c": []}
        result = topological_sort(adjacency)
        assert set(result) == {"a", "b", "c"}

    def test_complex_dag(self):
        """A more complex DAG."""
        adjacency = {
            "a": ["b", "c"],
            "b": ["d"],
            "c": ["d"],
            "d": [],
            "e": ["a"]
        }
        result = topological_sort(adjacency)
        # e is independent (in-degree 0)
        assert result[0] == "e"
        # a depends on e (e -> a)
        assert result.index("e") < result.index("a")
        # b and c depend on a
        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        # d depends on b, c
        assert result.index("b") < result.index("d")
        assert result.index("c") < result.index("d")

    def test_cycle_detection(self):
        """Graph with a cycle raises CyclicDependencyError."""
        adjacency = {"a": ["b"], "b": ["a"]}
        with pytest.raises(CyclicDependencyError, match="forms a cycle"):
            topological_sort(adjacency)

    def test_resolves_implicit_sinks(self):
        """Dependencies pointing to nodes that don't exist in the keys are treated as sinks."""
        adjacency = {"a": ["b"]} # 'b' is not a key
        result = topological_sort(adjacency)
        # a -> b, so a must be before b
        assert result.index("a") < result.index("b")


class TestDetectCycle:
    """Tests for cycle detection in adjacency list."""

    def test_detects_simple_cycle(self):
        adjacency = {"a": ["b"], "b": ["a"]}
        assert detect_cycle_in_adjacency(adjacency) is not None

    def test_no_cycle(self):
        adjacency = {"a": ["b"], "b": ["c"], "c": []}
        assert detect_cycle_in_adjacency(adjacency) is None

    def test_self_loop(self):
        adjacency = {"a": ["a"]}
        assert detect_cycle_in_adjacency(adjacency) is not None


class TestBuildFullDag:
    """Tests for assembling the global column DAG."""

    def test_builds_correct_hierarchy_dependencies(self):
        """Dimension group hierarchies imply dependencies (child depends on parent)."""
        groups = {
            "entity": DimensionGroup(
                name="entity",
                root="hospital",
                columns=["hospital", "department", "ward"],
                hierarchy=["hospital", "department", "ward"]
            )
        }
        deps = []
        measure_dag = {}
        
        columns = {
            "hospital": {"parent": None},
            "department": {"parent": "hospital"},
            "ward": {"parent": "department"}
        }

        adjacency = build_full_dag(columns, groups, deps, measure_dag)
        
        # 'department' depends on 'hospital', so hospital -> department
        assert "department" in adjacency["hospital"]
        # 'ward' depends on 'department', so department -> ward
        assert "ward" in adjacency["department"]
        # 'ward' is a leaf
        assert adjacency["ward"] == []

    def test_builds_group_dependencies(self):
        """Group dependencies link roots of different groups."""
        groups = {
            "entity": DimensionGroup(name="entity", root="hospital", columns=["hospital"], hierarchy=["hospital"]),
            "patient": DimensionGroup(name="patient", root="severity", columns=["severity"], hierarchy=["severity"])
        }
        deps = [
            GroupDependency("severity", ["hospital"], {})
        ]
        measure_dag = {}
        columns = {
            "hospital": {"group": "entity"},
            "severity": {"group": "patient"}
        }
        
        adjacency = build_full_dag(columns, groups, deps, measure_dag)
        # 'severity' depends on 'hospital'
        assert "severity" in adjacency["hospital"]
        assert adjacency["severity"] == []

    def test_builds_measure_dag(self):
        """Measures specifying their own DAG."""
        groups = {}
        deps = []
        measure_dag = {
            "cost": ["wait"],
            "wait": []
        }
        columns = {
            "cost": {"type": "measure"},
            "wait": {"type": "measure"}
        }
        
        adjacency = build_full_dag(columns, groups, deps, measure_dag)
        
        assert "wait" in adjacency["cost"]
        assert adjacency["wait"] == []

    def test_all_components_combined(self):
        """End-to-end integration of all DAG components."""
        groups = {
            "g1": DimensionGroup(name="g1", root="root1", columns=["root1", "child1"], hierarchy=["root1", "child1"]),
            "g2": DimensionGroup(name="g2", root="root2", columns=["root2"], hierarchy=["root2"])
        }
        deps = [GroupDependency("root2", ["root1"], {})]
        measure_dag = {
            "measure1": ["child1", "root2"],
            "measure2": ["measure1"]
        }
        columns = {
            "root1": {"parent": None, "type": "categorical"},
            "child1": {"parent": "root1", "type": "categorical"},
            "root2": {"parent": None, "type": "categorical"},
            "measure1": {"type": "measure"},
            "measure2": {"type": "measure"}
        }
        
        adjacency = build_full_dag(columns, groups, deps, measure_dag)
        
        assert adjacency["root1"] == ["child1", "root2"]
        assert "child1" in adjacency["root1"]
        assert "root2" in adjacency["root1"]
        assert "child1" in adjacency["measure1"]
        assert "root2" in adjacency["measure1"]
        assert "measure1" in adjacency["measure2"]

    def test_cycle_raises_error(self):
        """Cycles correctly bubble up from build_full_dag."""
        # Create a cycle via group dependencies
        groups = {
            "g1": DimensionGroup(name="g1", root="r1", columns=["r1"], hierarchy=["r1"]),
            "g2": DimensionGroup(name="g2", root="r2", columns=["r2"], hierarchy=["r2"])
        }
        deps = [
            GroupDependency("r2", ["r1"], {}),
            GroupDependency("r1", ["r2"], {})
        ]
        columns = {"r1": {}, "r2": {}}
        
        with pytest.raises(CyclicDependencyError):
            build_full_dag(columns, groups, deps, {})
