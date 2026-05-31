"""Round-trip tests for raw_declarations JSON (de)serialization.

Regression coverage for the JSON-key-stringify bug: ``json.dumps`` forces every
dict key to ``str``, but a categorical's ``values`` keep their declared dtype.
So an int-valued parent (e.g. ``year=[2023, 2024]``) whose conditional weights
were declared with int keys comes back string-keyed and never matches the int
column in ``skeleton.sample_dependent_root`` (``parent_values == parent_val``),
silently producing an all-None dependent column (and crashing any downstream
structural effect keyed on it). ``declarations_from_json`` now re-coerces those
keys to the parent column's declared dtype.

Before this suite there was NO serialization round-trip test at all — which is
why the bug shipped.
"""
from __future__ import annotations

import json

from pipeline.phase_2.engine.generator import run_pipeline
from pipeline.phase_2.sdk.simulator import FactTableSimulator
from pipeline.phase_2.serialization import (
    declarations_from_json,
    declarations_to_json,
)


def _extract(sim: FactTableSimulator) -> dict:
    return {
        "columns": sim._columns,
        "groups": sim._groups,
        "group_dependencies": sim._group_dependencies,
        "measure_dag": sim._measure_dag,
        "target_rows": sim.target_rows,
        "patterns": sim._patterns,
        "seed": sim.seed,
        "orthogonal_pairs": sim._orthogonal_pairs,
    }


def _disk_roundtrip(raw: dict) -> dict:
    """Simulate the real Stage-1 → disk → Stage-2 path: to_json, through actual
    json.dumps/loads (this is what stringifies dict keys), then from_json."""
    on_disk = json.loads(json.dumps(declarations_to_json(raw)))
    return on_disk, declarations_from_json(on_disk)


def _generate(raw2: dict):
    return run_pipeline(
        columns=raw2["columns"],
        groups=raw2["groups"],
        group_dependencies=raw2["group_dependencies"],
        measure_dag=raw2["measure_dag"],
        target_rows=raw2["target_rows"],
        seed=raw2.get("seed", 42),
        patterns=raw2.get("patterns", []),
        realism_config=None,
        orthogonal_pairs=raw2.get("orthogonal_pairs", []),
    )


def test_int_parent_group_dep_roundtrip():
    """int-valued `year` as a cross-group dependency parent must survive the
    JSON round-trip: the dependent column stays fully populated (no all-None)."""
    sim = FactTableSimulator(target_rows=200, seed=42)
    sim.add_category("year", values=[2023, 2024], weights=[0.5, 0.5], group="cal")
    sim.add_category(
        "observation_type",
        values=["X-ray", "Weak-lensing", "SZ"],
        weights=[0.35, 0.35, 0.3],
        group="method",
    )
    sim.add_group_dependency(
        "observation_type",
        on=["year"],
        conditional_weights={
            2023: {"X-ray": 0.40, "Weak-lensing": 0.30, "SZ": 0.30},
            2024: {"X-ray": 0.20, "Weak-lensing": 0.40, "SZ": 0.40},
        },
    )

    raw = _extract(sim)
    on_disk, raw2 = _disk_roundtrip(raw)

    # The on-disk JSON stringifies the cw keys (the root of the bug)...
    disk_keys = list(on_disk["group_dependencies"][0]["conditional_weights"].keys())
    assert disk_keys == ["2023", "2024"], disk_keys
    # ...and from_json coerces them back to the int dtype of the `year` column.
    gd = raw2["group_dependencies"][0]
    assert set(gd.conditional_weights.keys()) == {2023, 2024}

    df, _ = _generate(raw2)
    assert df["observation_type"].isna().sum() == 0, "dependent column went all-None"
    assert set(df["observation_type"].unique()) <= {"X-ray", "Weak-lensing", "SZ"}


def test_string_parent_group_dep_roundtrip_noop():
    """String-valued parents must be untouched by the coercion (no over-normalization)."""
    sim = FactTableSimulator(target_rows=200, seed=42)
    sim.add_category("season", values=["Wet", "Dry"], weights=[0.5, 0.5], group="cal")
    sim.add_category(
        "method", values=["A", "B"], weights=[0.5, 0.5], group="m",
    )
    sim.add_group_dependency(
        "method",
        on=["season"],
        conditional_weights={
            "Wet": {"A": 0.7, "B": 0.3},
            "Dry": {"A": 0.4, "B": 0.6},
        },
    )

    raw = _extract(sim)
    _, raw2 = _disk_roundtrip(raw)

    gd = raw2["group_dependencies"][0]
    assert set(gd.conditional_weights.keys()) == {"Wet", "Dry"}  # unchanged strings
    df, _ = _generate(raw2)
    assert df["method"].isna().sum() == 0
    assert set(df["method"].unique()) <= {"A", "B"}


def test_int_parent_child_weights_roundtrip():
    """Within-group child categorical with int-parent dict weights: same bug
    class, same fix (covers the second coercion site)."""
    sim = FactTableSimulator(target_rows=300, seed=42)
    sim.add_category("tier", values=[1, 2, 3], weights=[0.4, 0.3, 0.3], group="g")
    sim.add_category(
        "plan",
        values=["Basic", "Pro"],
        weights={1: [0.8, 0.2], 2: [0.5, 0.5], 3: [0.2, 0.8]},
        group="g",
        parent="tier",
    )

    raw = _extract(sim)
    _, raw2 = _disk_roundtrip(raw)

    # Child weights keys re-coerced to the int dtype of the `tier` parent.
    assert set(raw2["columns"]["plan"]["weights"].keys()) == {1, 2, 3}
    df, _ = _generate(raw2)
    assert df["plan"].isna().sum() == 0, "child column went all-None"
    assert set(df["plan"].unique()) <= {"Basic", "Pro"}
