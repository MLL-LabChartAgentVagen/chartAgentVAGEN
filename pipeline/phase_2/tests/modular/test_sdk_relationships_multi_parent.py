"""Tests for DS-4 multi-column ``add_group_dependency`` declaration.

Covers nested-dict ``conditional_weights``, full Cartesian coverage,
per-leaf normalization, multi-parent DAG cycle detection, and
multi-parent orthogonal-conflict detection.
"""
from __future__ import annotations

from collections import OrderedDict

import pandas as pd
import pytest

from pipeline.phase_2.exceptions import CyclicDependencyError
from pipeline.phase_2.sdk.relationships import (
    add_group_dependency,
    declare_orthogonal,
)
from pipeline.phase_2.types import DimensionGroup, GroupDependency
from pipeline.phase_2.validation.statistical import (
    check_group_dependency_transitions,
    max_conditional_deviation,
)


# =====================================================================
# Fixtures
# =====================================================================

def _make_two_parent_registry() -> tuple[
    OrderedDict[str, dict],
    dict[str, DimensionGroup],
]:
    """Build a column + group registry with two parent roots and one child root.

    Layout:
      group "patient" -> root "severity" (values: Mild, Moderate)
      group "entity"  -> root "hospital" (values: Xiehe, Mayo)
      group "finance" -> root "payment"  (values: Insurance, Self-Pay)
    """
    columns: OrderedDict[str, dict] = OrderedDict()
    columns["severity"] = {
        "group": "patient", "type": "categorical",
        "values": ["Mild", "Moderate"], "parent": None,
    }
    columns["hospital"] = {
        "group": "entity", "type": "categorical",
        "values": ["Xiehe", "Mayo"], "parent": None,
    }
    columns["payment"] = {
        "group": "finance", "type": "categorical",
        "values": ["Insurance", "Self-Pay"], "parent": None,
    }

    groups = {
        "patient": DimensionGroup(
            name="patient", root="severity",
            columns=["severity"], hierarchy=["severity"],
        ),
        "entity": DimensionGroup(
            name="entity", root="hospital",
            columns=["hospital"], hierarchy=["hospital"],
        ),
        "finance": DimensionGroup(
            name="finance", root="payment",
            columns=["payment"], hierarchy=["payment"],
        ),
    }
    return columns, groups


def _make_three_parent_registry() -> tuple[
    OrderedDict[str, dict],
    dict[str, DimensionGroup],
]:
    """Two-parent registry plus a third parent root in its own group."""
    columns, groups = _make_two_parent_registry()
    columns["region"] = {
        "group": "geo", "type": "categorical",
        "values": ["North", "South"], "parent": None,
    }
    groups["geo"] = DimensionGroup(
        name="geo", root="region",
        columns=["region"], hierarchy=["region"],
    )
    return columns, groups


# =====================================================================
# Declaration: happy path
# =====================================================================

class TestMultiParentDeclaration:

    def test_two_parent_full_coverage_succeeds(self):
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw = {
            "Mild":     {"Xiehe": {"Insurance": 0.8, "Self-Pay": 0.2},
                         "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3}},
            "Moderate": {"Xiehe": {"Insurance": 0.6, "Self-Pay": 0.4},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw,
        )
        assert len(deps) == 1
        d = deps[0]
        assert d.child_root == "payment"
        assert d.on == ["severity", "hospital"]
        # Each leaf is normalized to sum 1.0
        for sev in ["Mild", "Moderate"]:
            for hosp in ["Xiehe", "Mayo"]:
                leaf = d.conditional_weights[sev][hosp]
                assert abs(sum(leaf.values()) - 1.0) < 1e-9
                assert set(leaf.keys()) == {"Insurance", "Self-Pay"}

    def test_three_parent_full_coverage_succeeds(self):
        columns, groups = _make_three_parent_registry()
        deps: list[GroupDependency] = []
        # 2x2x2 nested (severity x hospital x region) -> child weights
        leaf = {"Insurance": 1.0, "Self-Pay": 1.0}  # normalized to 0.5/0.5
        cw = {
            sev: {hosp: {reg: dict(leaf)
                         for reg in ["North", "South"]}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment",
            on=["severity", "hospital", "region"],
            conditional_weights=cw,
        )
        assert len(deps) == 1
        # Drill to one leaf and confirm normalization
        leaf_out = deps[0].conditional_weights["Mild"]["Xiehe"]["North"]
        assert leaf_out == {"Insurance": 0.5, "Self-Pay": 0.5}

    def test_normalization_at_each_leaf(self):
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw = {
            "Mild":     {"Xiehe": {"Insurance": 80, "Self-Pay": 20},
                         "Mayo":  {"Insurance": 4,  "Self-Pay": 1}},
            "Moderate": {"Xiehe": {"Insurance": 1,  "Self-Pay": 1},
                         "Mayo":  {"Insurance": 3,  "Self-Pay": 7}},
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw,
        )
        normed = deps[0].conditional_weights
        assert normed["Mild"]["Xiehe"] == {"Insurance": 0.8, "Self-Pay": 0.2}
        assert normed["Mild"]["Mayo"] == {"Insurance": 0.8, "Self-Pay": 0.2}
        assert normed["Moderate"]["Xiehe"] == {"Insurance": 0.5, "Self-Pay": 0.5}
        assert normed["Moderate"]["Mayo"] == {"Insurance": 0.3, "Self-Pay": 0.7}


# =====================================================================
# Declaration: error paths
# =====================================================================

class TestMultiParentValidationErrors:

    def test_missing_parent_at_depth_1_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {
            # "Moderate" key is missing
            "Mild": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                     "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )
        msg = str(exc.value)
        assert "depth 0" in msg
        assert "severity" in msg
        assert "Moderate" in msg

    def test_missing_parent_at_depth_2_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {
            "Mild":     {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
            # "Mayo" missing under "Moderate"
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )
        msg = str(exc.value)
        assert "['Moderate']" in msg
        assert "depth 1" in msg
        assert "hospital" in msg
        assert "Mayo" in msg

    def test_missing_child_at_leaf_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {
            "Mild":     {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         # "Self-Pay" missing
                         "Mayo":  {"Insurance": 1.0}},
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )
        msg = str(exc.value)
        assert "['Mild']['Mayo']" in msg
        assert "Self-Pay" in msg
        assert "missing child values" in msg

    def test_extra_parent_key_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {
            "Mild":     {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
            # extra outer key not in severity values
            "Critical": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )
        msg = str(exc.value)
        assert "not in parent 'severity' values" in msg
        assert "Critical" in msg

    def test_negative_weight_at_leaf_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {
            "Mild":     {"Xiehe": {"Insurance": -0.1, "Self-Pay": 1.1},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )
        assert "negative" in str(exc.value).lower()

    def test_empty_on_raises(self):
        columns, groups = _make_two_parent_registry()
        with pytest.raises(ValueError, match="must contain at least one column"):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=[],
                conditional_weights={},
            )

    def test_empty_conditional_weights_raises(self):
        columns, groups = _make_two_parent_registry()
        with pytest.raises(ValueError, match="is empty"):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity", "hospital"],
                conditional_weights={},
            )


# =====================================================================
# Backward compatibility (single-parent)
# =====================================================================

class TestSingleParentBackwardCompat:

    def test_single_column_normalized_output_unchanged(self):
        """`on=["severity"]` with the OLD flat dict shape produces
        byte-identical normalized output to v1."""
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw = {
            "Mild":     {"Insurance": 8, "Self-Pay": 2},
            "Moderate": {"Insurance": 5, "Self-Pay": 5},
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity"],
            conditional_weights=cw,
        )
        assert deps[0].on == ["severity"]
        # Pre-DS-4 produced exactly this normalized output.
        assert deps[0].conditional_weights == {
            "Mild":     {"Insurance": 0.8, "Self-Pay": 0.2},
            "Moderate": {"Insurance": 0.5, "Self-Pay": 0.5},
        }

    def test_single_column_missing_parent_value_raises(self):
        columns, groups = _make_two_parent_registry()
        cw = {"Mild": {"Insurance": 0.5, "Self-Pay": 0.5}}
        with pytest.raises(ValueError) as exc:
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=[],
                child_root="payment", on=["severity"],
                conditional_weights=cw,
            )
        assert "Moderate" in str(exc.value)


# =====================================================================
# Multi-parent DAG cycle + orthogonal conflict
# =====================================================================

class TestMultiParentDagAndConflict:

    def test_multi_parent_dag_cycle_raises(self):
        """Declaring `payment.on=[severity, hospital]` then
        `severity.on=[payment]` must raise — the second edge would
        close the cycle severity -> payment -> severity."""
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw1 = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw1,
        )
        # Now try to declare severity depends on payment -> cycle.
        cw2 = {pay: {"Mild": 0.5, "Moderate": 0.5}
               for pay in ["Insurance", "Self-Pay"]}
        with pytest.raises(CyclicDependencyError):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=deps, orthogonal_pairs=[],
                child_root="severity", on=["payment"],
                conditional_weights=cw2,
            )

    def test_multi_parent_dag_cycle_via_secondary_parent_raises(self):
        """Existing dep has hospital as `on[1]`. A new edge
        hospital -> ??? -> ... -> severity must still detect cycles
        via the non-first parent. Direct case: hospital.on=[payment]."""
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw1 = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw1,
        )
        # hospital -> payment (existing, via on[1]) and now we try
        # payment -> hospital, which closes the cycle. Pre-fix this
        # was missed because check_root_dag_acyclic only registered
        # dep.on[0] = severity.
        cw2 = {pay: {"Xiehe": 0.5, "Mayo": 0.5}
               for pay in ["Insurance", "Self-Pay"]}
        with pytest.raises(CyclicDependencyError):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=deps, orthogonal_pairs=[],
                child_root="hospital", on=["payment"],
                conditional_weights=cw2,
            )

    def test_multi_parent_orthogonal_conflict_via_first_parent_raises(self):
        columns, groups = _make_two_parent_registry()
        # Declare orthogonal first, then try a multi-parent dep that
        # touches that orthogonal pair via on[0]=severity. Must raise.
        ortho: list = []
        declare_orthogonal(
            groups=groups, orthogonal_pairs=ortho,
            group_dependencies=[], columns=columns,
            group_a="patient", group_b="finance", rationale="test",
        )
        cw = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        with pytest.raises(ValueError, match="orthogonal"):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=ortho,
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )

    def test_multi_parent_orthogonal_conflict_via_second_parent_raises(self):
        """Orthogonal between (payment_group, hospital_group). A
        multi-parent dep child=payment, on=[severity, hospital]
        creates a payment<-hospital edge via on[1]. Pre-fix this was
        missed because add_group_dependency only checked on[0]."""
        columns, groups = _make_two_parent_registry()
        ortho: list = []
        declare_orthogonal(
            groups=groups, orthogonal_pairs=ortho,
            group_dependencies=[], columns=columns,
            group_a="entity", group_b="finance", rationale="test",
        )
        cw = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        with pytest.raises(ValueError, match="orthogonal"):
            add_group_dependency(
                columns=columns, groups=groups,
                group_dependencies=[], orthogonal_pairs=ortho,
                child_root="payment", on=["severity", "hospital"],
                conditional_weights=cw,
            )

    def test_declare_orthogonal_after_multi_parent_dep_via_secondary_raises(self):
        """Inverse direction of the conflict: multi-parent dep first
        (touching hospital via on[1]), then attempt to declare
        (entity, finance) orthogonal. Pre-fix this was falsely allowed
        because _check_dependency_conflict only inspected dep.on[0]."""
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw,
        )
        with pytest.raises(ValueError, match="already have a "):
            declare_orthogonal(
                groups=groups, orthogonal_pairs=[],
                group_dependencies=deps, columns=columns,
                group_a="entity", group_b="finance", rationale="test",
            )


# =====================================================================
# to_metadata deep-copy isolation
# =====================================================================

class TestToMetadataDeepCopy:

    def test_to_metadata_deep_copies_nested_weights(self):
        columns, groups = _make_two_parent_registry()
        deps: list[GroupDependency] = []
        cw = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        add_group_dependency(
            columns=columns, groups=groups,
            group_dependencies=deps, orthogonal_pairs=[],
            child_root="payment", on=["severity", "hospital"],
            conditional_weights=cw,
        )
        meta = deps[0].to_metadata()
        # Mutating any nesting level of the metadata copy must not
        # leak back into the GroupDependency.
        meta["conditional_weights"]["Mild"]["Xiehe"]["Insurance"] = 0.0
        assert (
            deps[0].conditional_weights["Mild"]["Xiehe"]["Insurance"] == 0.5
        )
        meta["conditional_weights"]["Mild"]["Xiehe"] = {"poison": 1.0}
        assert (
            "Insurance"
            in deps[0].conditional_weights["Mild"]["Xiehe"]
        )


# =====================================================================
# L2: max_conditional_deviation + check_group_dependency_transitions
# =====================================================================

class TestL2MultiParentDeviation:

    def test_max_conditional_deviation_depth_1_unchanged(self):
        observed = {
            "Mild":     {"Insurance": 0.8, "Self-Pay": 0.2},
            "Moderate": {"Insurance": 0.5, "Self-Pay": 0.5},
        }
        declared = {
            "Mild":     {"Insurance": 0.8, "Self-Pay": 0.2},
            "Moderate": {"Insurance": 0.5, "Self-Pay": 0.5},
        }
        assert max_conditional_deviation(observed, declared) == 0.0
        # One leaf diverges by 0.1
        observed["Moderate"]["Insurance"] = 0.6
        observed["Moderate"]["Self-Pay"] = 0.4
        assert abs(max_conditional_deviation(observed, declared) - 0.1) < 1e-9

    def test_max_conditional_deviation_depth_2_detects_divergence(self):
        observed = {
            "Mild":     {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3}},
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        declared = {
            "Mild":     {"Xiehe": {"Insurance": 0.8, "Self-Pay": 0.2},
                         "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3}},
            "Moderate": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5},
                         "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
        }
        assert abs(max_conditional_deviation(observed, declared) - 0.3) < 1e-9

    def test_max_conditional_deviation_depth_3(self):
        leaf_eq = {"Insurance": 0.5, "Self-Pay": 0.5}
        leaf_div = {"Insurance": 0.7, "Self-Pay": 0.3}
        observed = {
            "Mild": {"Xiehe": {"North": leaf_eq, "South": leaf_eq},
                     "Mayo":  {"North": leaf_eq, "South": leaf_eq}},
            "Moderate": {"Xiehe": {"North": leaf_eq, "South": leaf_eq},
                         "Mayo":  {"North": leaf_eq, "South": leaf_eq}},
        }
        declared = {
            "Mild": {"Xiehe": {"North": leaf_eq, "South": leaf_div},
                     "Mayo":  {"North": leaf_eq, "South": leaf_eq}},
            "Moderate": {"Xiehe": {"North": leaf_eq, "South": leaf_eq},
                         "Mayo":  {"North": leaf_eq, "South": leaf_eq}},
        }
        # |0.5 - 0.7| = 0.2 at the diverging leaf
        assert abs(max_conditional_deviation(observed, declared) - 0.2) < 1e-9

    def test_check_group_dependency_transitions_two_parent_pass(self):
        import pandas as pd

        # Declared distribution: 50/50 everywhere.
        declared = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        meta = {
            "group_dependencies": [{
                "child_root": "payment",
                "on": ["severity", "hospital"],
                "conditional_weights": declared,
            }],
        }
        # Build a df where each (sev, hosp) cell has exactly 50/50.
        rows = []
        for sev in ["Mild", "Moderate"]:
            for hosp in ["Xiehe", "Mayo"]:
                for _ in range(50):
                    rows.append((sev, hosp, "Insurance"))
                for _ in range(50):
                    rows.append((sev, hosp, "Self-Pay"))
        df = pd.DataFrame(rows, columns=["severity", "hospital", "payment"])

        checks = check_group_dependency_transitions(df, meta)
        assert len(checks) == 1
        assert checks[0].name == "group_dep_payment"
        assert checks[0].passed is True
        assert "severity" in checks[0].detail
        assert "hospital" in checks[0].detail

    def test_check_group_dependency_transitions_two_parent_fail(self):
        import pandas as pd

        declared = {
            sev: {hosp: {"Insurance": 0.5, "Self-Pay": 0.5}
                  for hosp in ["Xiehe", "Mayo"]}
            for sev in ["Mild", "Moderate"]
        }
        meta = {
            "group_dependencies": [{
                "child_root": "payment",
                "on": ["severity", "hospital"],
                "conditional_weights": declared,
            }],
        }
        # All-Insurance under (Mild, Xiehe) -> 1.0 vs declared 0.5
        # observed deviation 0.5 > threshold 0.10.
        rows = []
        for _ in range(100):
            rows.append(("Mild", "Xiehe", "Insurance"))
        for sev, hosp in [("Mild", "Mayo"), ("Moderate", "Xiehe"),
                          ("Moderate", "Mayo")]:
            for _ in range(50):
                rows.append((sev, hosp, "Insurance"))
            for _ in range(50):
                rows.append((sev, hosp, "Self-Pay"))
        df = pd.DataFrame(rows, columns=["severity", "hospital", "payment"])
        checks = check_group_dependency_transitions(df, meta)
        assert checks[0].passed is False
        assert "severity" in checks[0].detail
        assert "hospital" in checks[0].detail

    def test_check_group_dependency_transitions_missing_column(self):
        import pandas as pd

        meta = {
            "group_dependencies": [{
                "child_root": "payment",
                "on": ["severity", "hospital"],
                "conditional_weights": {
                    "Mild": {"Xiehe": {"Insurance": 0.5, "Self-Pay": 0.5}},
                },
            }],
        }
        # df is missing "hospital" column
        df = pd.DataFrame({
            "severity": ["Mild"] * 10,
            "payment": ["Insurance"] * 10,
        })
        checks = check_group_dependency_transitions(df, meta)
        assert len(checks) == 1
        assert checks[0].passed is False
        assert "hospital" in checks[0].detail


# =====================================================================
# Closes T1.5 of docs/TEST_AUDIT_2026-05-07.md.
#
# Spec §2.1.2 headline: "If Group A ⊥ Group B, then ALL cross-group
# pairs are automatically independent — no need to enumerate." With
# entity = [hospital, department] and patient = [severity], a single
# `declare_orthogonal("entity","patient")` must induce independence at
# the *child* pair (department, severity) — not just the root pair.
#
# The pre-existing tests in this file cover orthogonal-vs-dependency
# CONFLICT detection. There is no positive test verifying that, after a
# successful declare_orthogonal, generated data actually exhibits
# child-pair independence. A latent regression where the engine wired
# orthogonality at root level only would slip through every existing
# test. The end-to-end test below closes the gap.
# =====================================================================


class TestDeclareOrthogonalChildPropagation:
    """Generate a 3000-row table with two hierarchical groups, declare
    a single group-level orthogonality, then verify chi-squared
    independence at each cross-group column pair (root×root, root×child,
    child×child)."""

    def test_independence_propagates_to_all_cross_group_pairs(self):
        import scipy.stats
        from pipeline.phase_2.sdk.simulator import FactTableSimulator

        sim = FactTableSimulator(target_rows=3000, seed=42)

        # entity group: hospital → department.
        sim.add_category(
            name="hospital",
            values=["Xiehe", "Mayo", "Tongren"],
            weights=[0.4, 0.4, 0.2],
            group="entity",
        )
        sim.add_category(
            name="department",
            values=["Internal", "Surgery"],
            # Within-parent weights — distinct per parent so the child's
            # marginal varies with hospital. Spec §2.1.2 hierarchy.
            weights={
                "Xiehe":   [0.7, 0.3],
                "Mayo":    [0.5, 0.5],
                "Tongren": [0.2, 0.8],
            },
            group="entity",
            parent="hospital",
        )

        # patient group: severity → acuity.
        sim.add_category(
            name="severity",
            values=["Mild", "Severe"],
            weights=[0.6, 0.4],
            group="patient",
        )
        sim.add_category(
            name="acuity",
            values=["Low", "High"],
            weights={
                "Mild":   [0.8, 0.2],
                "Severe": [0.2, 0.8],
            },
            group="patient",
            parent="severity",
        )

        # SINGLE orthogonal declaration — spec promises this propagates
        # automatically to every cross-group pair.
        sim.declare_orthogonal(
            "entity", "patient",
            rationale="patient severity is independent of which hospital",
        )

        df, _ = sim.generate()

        # Every cross-group pair must be independent (chi² p > 0.05).
        cross_pairs = [
            ("hospital", "severity"),    # root × root
            ("hospital", "acuity"),      # root × child
            ("department", "severity"),  # child × root
            ("department", "acuity"),    # child × child
        ]
        for col_a, col_b in cross_pairs:
            ct = pd.crosstab(df[col_a], df[col_b])
            assert ct.shape[0] >= 2 and ct.shape[1] >= 2, \
                f"degenerate contingency for ({col_a}, {col_b}): {ct.shape}"
            _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
            assert p_val > 0.05, (
                f"Cross-group pair ({col_a}, {col_b}) failed χ² independence: "
                f"p={p_val:.4f} (expected p > 0.05). "
                f"Spec §2.1.2 promises automatic propagation to ALL cross-group "
                f"pairs after declare_orthogonal('entity', 'patient')."
            )

    def test_within_group_pairs_are_NOT_forced_independent(self):
        """Sanity check that orthogonality is *cross-group only*. Within
        the entity group, hospital→department has declared per-parent
        weights, so χ² should reject independence (i.e., department
        depends on hospital). If this passed independence too, the
        engine would be over-applying orthogonality."""
        import scipy.stats
        from pipeline.phase_2.sdk.simulator import FactTableSimulator

        sim = FactTableSimulator(target_rows=3000, seed=42)
        sim.add_category(
            name="hospital",
            values=["Xiehe", "Mayo", "Tongren"],
            weights=[0.4, 0.4, 0.2],
            group="entity",
        )
        sim.add_category(
            name="department",
            values=["Internal", "Surgery"],
            weights={
                "Xiehe":   [0.7, 0.3],
                "Mayo":    [0.5, 0.5],
                "Tongren": [0.2, 0.8],
            },
            group="entity",
            parent="hospital",
        )
        sim.add_category(
            name="severity",
            values=["Mild", "Severe"],
            weights=[0.6, 0.4],
            group="patient",
        )
        sim.declare_orthogonal("entity", "patient", rationale="indep")

        df, _ = sim.generate()
        ct = pd.crosstab(df["hospital"], df["department"])
        _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
        # Within-entity: declared weights differ per parent, so we EXPECT
        # dependency. Orthogonality must not have leaked into the entity
        # group's internal hierarchy.
        assert p_val <= 0.05, (
            f"Within-group hospital→department dependency was wiped out "
            f"(p={p_val:.4f}). Orthogonality must be cross-group only."
        )
