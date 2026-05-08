"""
Tests for SDK Column operations.

Tested functions:
- add_category
- add_temporal
- add_measure
- add_measure_structural
"""
from __future__ import annotations

import pytest
from collections import OrderedDict

from pipeline.phase_2.exceptions import EmptyValuesError, DuplicateGroupRootError, DuplicateColumnError
from pipeline.phase_2.types import DimensionGroup
from pipeline.phase_2.sdk.columns import (
    add_category,
    add_temporal,
    add_measure,
    add_measure_structural,
)


class TestAddCategory:
    
    def test_add_root_categorical_column(self):
        columns = OrderedDict()
        groups = {}
        
        add_category(
            columns=columns,
            groups=groups,
            name="hospital",
            values=["A", "B"],
            weights=[0.6, 0.4],
            group="entity",
            parent=None
        )
        
        assert "hospital" in columns
        assert columns["hospital"]["type"] == "categorical"
        assert columns["hospital"]["weights"] == [0.6, 0.4]
        
        assert "entity" in groups
        assert groups["entity"].root == "hospital"
        assert groups["entity"].columns == ["hospital"]
        assert groups["entity"].hierarchy == ["hospital"]

    def test_add_child_categorical_column(self):
        columns = OrderedDict({
            "hospital": {"group": "entity", "type": "categorical", "values": ["A", "B"]}
        })
        groups = {
            "entity": DimensionGroup(name="entity", root="hospital", columns=["hospital"], hierarchy=["hospital"])
        }
        
        add_category(
            columns=columns,
            groups=groups,
            name="ward",
            values=["ER", "ICU"],
            weights={"A": [0.8, 0.2], "B": [0.5, 0.5]},
            group="entity",
            parent="hospital"
        )
        
        assert "ward" in columns
        assert columns["ward"]["parent"] == "hospital"
        assert columns["ward"]["weights"]["A"] == [0.8, 0.2]
        
        assert "ward" in groups["entity"].columns
        assert "ward" in groups["entity"].hierarchy

    def test_duplicate_root_rejected(self):
        columns = OrderedDict({"hospital": {"group": "entity"}})
        groups = {"entity": DimensionGroup(name="entity", root="hospital", columns=["hospital"], hierarchy=["hospital"])}
        
        with pytest.raises(DuplicateGroupRootError, match="already has root"):
            add_category(columns, groups, "another_root", ["X"], [1.0], "entity", parent=None)

    def test_empty_values_rejected(self):
        with pytest.raises(EmptyValuesError):
            add_category(OrderedDict(), {}, "bad", [], [], "entity")


class TestAddTemporal:
    
    def test_add_temporal_with_derive(self):
        columns = OrderedDict()
        groups = {}
        
        add_temporal(
            columns=columns,
            groups=groups,
            name="admit_date",
            start="2024-01-01",
            end="2024-12-31",
            freq="D",
            derive=["day_of_week", "month"]
        )
        
        # Root column
        assert "admit_date" in columns
        assert columns["admit_date"]["type"] == "temporal"
        
        # Derived columns
        assert "admit_date_day_of_week" in columns
        assert columns["admit_date_day_of_week"]["derivation"] == "day_of_week"
        assert columns["admit_date_month"]["derivation"] == "month"
        
        # Group handling
        assert "time" in groups
        assert groups["time"].root == "admit_date"
        assert "admit_date_day_of_week" in groups["time"].columns
        # Temporal hierarchy only contains root
        assert groups["time"].hierarchy == ["admit_date"]

    def test_invalid_date_format_rejected(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            add_temporal(OrderedDict(), {}, "date", "2024/01/01", "2024-12-31", "D")

    def test_end_before_start_rejected(self):
        with pytest.raises(ValueError, match="must be before end"):
            add_temporal(OrderedDict(), {}, "date", "2024-12-31", "2024-01-01", "D")


class TestAddMeasure:
    
    def test_add_stochastic_measure(self):
        columns = OrderedDict()
        add_measure(
            columns=columns,
            name="cost",
            family="gaussian",
            param_model={"mu": 100, "sigma": 15},
        )

        assert "cost" in columns
        assert columns["cost"]["type"] == "measure"
        assert columns["cost"]["measure_type"] == "stochastic"
        # `scale` kwarg was removed (TODO [M?-NC-scale]); no longer stored.
        assert "scale" not in columns["cost"]

    def test_add_measure_rejects_scale_kwarg(self):
        """The removed kwarg should raise TypeError at call time so the
        retry feedback can explain to the LLM that scale is not supported."""
        import pytest
        columns = OrderedDict()
        with pytest.raises(TypeError, match="scale"):
            add_measure(
                columns=columns,
                name="cost",
                family="gaussian",
                param_model={"mu": 100, "sigma": 15},
                scale=1.5,
            )


class TestAddMeasureStructural:
    
    def test_add_structural_measure(self):
        columns = OrderedDict({
            "age": {"type": "measure"},
            "mock_cat": {"type": "categorical", "values": ["A"]}
        })
        measure_dag = {}
        
        add_measure_structural(
            columns=columns,
            measure_dag=measure_dag,
            name="risk",
            formula="age * factor + noise_1",
            effects={"factor": {"A": 1.2}}, # We assume 'A' matches some categorical col if validated against one, but here we only validate formula inclusion for now. Wait, validate_structural_effects checks `columns` for match.
        ) # If we don't declare a categorical col with value "A", it might fail validation. Let's see. 
          # Ah! add_measure_structural calls `_val.validate_structural_effects`. So it will throw UndefinedEffectError if categorical doesn't match.

    def test_structural_with_valid_effects(self):
        columns = OrderedDict({
            "age": {"type": "measure"},
            "hospital": {"type": "categorical", "values": ["A", "B"]}
        })
        measure_dag = {}
        
        add_measure_structural(
            columns=columns,
            measure_dag=measure_dag,
            name="risk",
            formula="age * factor",
            effects={"factor": {"A": 1.2, "B": 0.8}}
        )
        
        assert "risk" in columns
        assert columns["risk"]["measure_type"] == "structural"
        assert "risk" in measure_dag["age"]

    def test_structural_formula_effect_mismatch(self):
        columns = OrderedDict({
            "hospital": {"type": "categorical", "values": ["A"]}
        })
        with pytest.raises(Exception): # UndefinedEffectError
            add_measure_structural(
                columns=columns,
                measure_dag={},
                name="risk",
                formula="100", # missing 'factor'
                effects={"factor": {"A": 1.2}}
            )


class TestAddCategoryWeightSafeguards:
    """Spec §2.1.1 — `add_category` auto-normalizes weights and rejects
    invalid weight vectors. Closes part of T1.9 in TEST_AUDIT_2026-05-07.md."""

    def test_unnormalized_weights_are_stored_normalized(self):
        """`weights=[1, 2, 1]` should be normalized to `[0.25, 0.5, 0.25]`
        per the spec safeguard table. Pre-existing tests use `[0.6, 0.4]`
        which is already normalized, so a regression where normalization
        was dropped (and weights stored verbatim) would slip through."""
        columns = OrderedDict()
        groups = {}
        add_category(
            columns=columns, groups=groups, name="hospital",
            values=["A", "B", "C"], weights=[1.0, 2.0, 1.0],
            group="entity", parent=None,
        )
        stored = columns["hospital"]["weights"]
        assert stored == pytest.approx([0.25, 0.5, 0.25]), (
            f"weights should auto-normalize to sum=1; got {stored}"
        )
        assert sum(stored) == pytest.approx(1.0)

    def test_all_zero_weights_rejected(self):
        with pytest.raises(ValueError, match="zero|normaliz"):
            add_category(
                OrderedDict(), {}, "bad",
                values=["A", "B"], weights=[0.0, 0.0],
                group="entity",
            )

    def test_negative_weights_rejected(self):
        with pytest.raises(ValueError, match="negative|>= 0"):
            add_category(
                OrderedDict(), {}, "bad",
                values=["A", "B"], weights=[1.0, -0.5],
                group="entity",
            )

    def test_weight_count_mismatch_rejected(self):
        # Spec §2.1.1: weight vector length must match values list.
        from pipeline.phase_2.exceptions import WeightLengthMismatchError
        with pytest.raises(WeightLengthMismatchError):
            add_category(
                OrderedDict(), {}, "bad",
                values=["A", "B", "C"], weights=[0.5, 0.5],
                group="entity",
            )


class TestAddMeasureFamilySafeguard:
    """Spec §2.1.1 — `add_measure` type-checks the `dist`/`family` argument
    (`Type-checks dist; blocks degenerate params`). The SDK rejects unknown
    families at declaration time so the LLM gets fast feedback rather than a
    deferred sampling-time crash. Closes part of T1.9."""

    def test_unknown_family_rejected_at_declaration(self):
        columns = OrderedDict()
        with pytest.raises(ValueError, match="Unsupported|family|Supported"):
            add_measure(
                columns=columns, name="x",
                family="not_a_distribution",
                param_model={"mu": 100.0, "sigma": 10.0},
            )

    def test_known_families_accepted(self):
        # Sanity guard so the negative test above isn't hiding a generic
        # "every family raises" behaviour. Limited to the two-param families
        # that share `mu`/`sigma`; poisson/exponential have their own param
        # keys covered elsewhere.
        for family in ("gaussian", "lognormal"):
            columns = OrderedDict()
            add_measure(
                columns=columns, name=f"m_{family}",
                family=family,
                param_model={"mu": 2.0, "sigma": 1.5},
            )
            assert columns[f"m_{family}"]["family"] == family


class TestAddTemporalFrequencySafeguard:
    """Spec §2.1.1 — `add_temporal` validates the frequency string. Closes
    part of T1.9 — the existing tests cover invalid date format and
    end-before-start, but not unsupported frequency tokens."""

    def test_unsupported_freq_string_rejected(self):
        with pytest.raises(ValueError):
            add_temporal(
                OrderedDict(), {}, name="d",
                start="2024-01-01", end="2024-12-31",
                freq="FORTNIGHTLY",  # not a valid pandas freq
            )
