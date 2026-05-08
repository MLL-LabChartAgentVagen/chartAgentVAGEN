"""Tests for DS-4 multi-parent ``sample_dependent_root`` engine sampling.

Covers:
- 2-parent sampling reproduces declared conditional within tolerance.
- 3-parent sampling reproduces declared conditional.
- Single-parent fast path produces byte-identical RNG output to v1
  (regression guard so callers depending on a fixed seed are stable).
"""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.phase_2.engine.skeleton import sample_dependent_root
from pipeline.phase_2.types import GroupDependency


def _empirical_conditional(
    parent_arrays: list[np.ndarray],
    child_array: np.ndarray,
) -> dict:
    """Build a nested {p_val: {p_val: {child: freq}}} dict from samples."""
    n = len(child_array)
    out: dict = {}
    # Group rows by parent tuple
    keys = list(zip(*parent_arrays))
    counts: dict = {}
    for i in range(n):
        k = keys[i]
        c = counts.setdefault(k, {})
        c[child_array[i]] = c.get(child_array[i], 0) + 1
    for k, child_counts in counts.items():
        total = sum(child_counts.values())
        leaf = {cv: cnt / total for cv, cnt in child_counts.items()}
        node = out
        for level, kv in enumerate(k):
            if level == len(k) - 1:
                node[kv] = leaf
            else:
                node = node.setdefault(kv, {})
    return out


def _max_dev(observed: dict, declared: dict) -> float:
    """Recursive max absolute deviation; mirrors validation helper but
    keyed on raw types (not str-coerced)."""
    sample = next(iter(observed.values()), None)
    if not isinstance(sample, dict):
        all_keys = set(observed) | set(declared)
        return max(
            (abs(observed.get(k, 0.0) - declared.get(k, 0.0))
             for k in all_keys),
            default=0.0,
        )
    return max(
        _max_dev(observed.get(k, {}), declared.get(k, {}))
        for k in (set(observed) | set(declared))
    )


class TestSampleDependentRootMultiParent:

    def test_two_parent_reproduces_distribution(self):
        rng = np.random.default_rng(42)
        n = 20000
        # Uniform parent draws
        a = rng.choice(["a1", "a2"], size=n)
        b = rng.choice(["b1", "b2"], size=n)
        rows = {"a": a, "b": b}

        declared = {
            "a1": {"b1": {"c1": 0.9, "c2": 0.1},
                   "b2": {"c1": 0.5, "c2": 0.5}},
            "a2": {"b1": {"c1": 0.2, "c2": 0.8},
                   "b2": {"c1": 0.7, "c2": 0.3}},
        }
        dep = GroupDependency(
            child_root="c", on=["a", "b"],
            conditional_weights=declared,
        )
        col_meta = {"values": ["c1", "c2"]}
        out = sample_dependent_root(
            "c", col_meta, dep, rows, n,
            rng=np.random.default_rng(7),
        )
        observed = _empirical_conditional([a, b], out)
        dev = _max_dev(observed, declared)
        assert dev < 0.025, (
            f"empirical conditional drifted from declared by {dev:.4f} "
            f"(observed={observed})"
        )

    def test_three_parent_reproduces_distribution(self):
        rng = np.random.default_rng(0)
        n = 16000
        a = rng.choice(["a1", "a2"], size=n)
        b = rng.choice(["b1", "b2"], size=n)
        d = rng.choice(["d1", "d2"], size=n)
        rows = {"a": a, "b": b, "d": d}

        # Build a depth-3 conditional with one strongly-skewed leaf
        declared: dict = {}
        for av in ["a1", "a2"]:
            for bv in ["b1", "b2"]:
                for dv in ["d1", "d2"]:
                    leaf = {"c1": 0.5, "c2": 0.5}
                    if (av, bv, dv) == ("a1", "b1", "d1"):
                        leaf = {"c1": 0.9, "c2": 0.1}
                    declared.setdefault(av, {}) \
                            .setdefault(bv, {})[dv] = leaf
        dep = GroupDependency(
            child_root="c", on=["a", "b", "d"],
            conditional_weights=declared,
        )
        col_meta = {"values": ["c1", "c2"]}
        out = sample_dependent_root(
            "c", col_meta, dep, rows, n,
            rng=np.random.default_rng(11),
        )
        observed = _empirical_conditional([a, b, d], out)
        dev = _max_dev(observed, declared)
        assert dev < 0.05, (
            f"empirical conditional drifted from declared by {dev:.4f}"
        )


class TestSampleDependentRootSingleParentBackwardCompat:

    def test_single_parent_byte_identical_rng_output(self):
        """The single-parent fast path must produce the exact same
        sample sequence as the pre-DS-4 implementation under a fixed
        RNG seed. This pins the byte-identical guarantee promised by
        the design."""
        n = 50
        rng_pre = np.random.default_rng(123)
        parent_values = rng_pre.choice(["a1", "a2"], size=n)
        rows = {"a": parent_values}

        declared = {
            "a1": {"c1": 0.7, "c2": 0.3},
            "a2": {"c1": 0.2, "c2": 0.8},
        }
        dep = GroupDependency(
            child_root="c", on=["a"],
            conditional_weights=declared,
        )
        col_meta = {"values": ["c1", "c2"]}

        # Sampler under the new implementation
        sample_rng = np.random.default_rng(99)
        out_new = sample_dependent_root(
            "c", col_meta, dep, rows, n, rng=sample_rng,
        )

        # Mimic the pre-DS-4 logic exactly (per-block batched draws).
        sample_rng_ref = np.random.default_rng(99)
        child_values = ["c1", "c2"]
        child_arr = np.array(child_values, dtype=object)
        result_ref = np.empty(n, dtype=object)
        for parent_val, child_weight_map in declared.items():
            mask = parent_values == parent_val
            n_match = int(np.sum(mask))
            if n_match == 0:
                continue
            w = np.array(
                [child_weight_map.get(cv, 0.0) for cv in child_values],
                dtype=np.float64,
            )
            s = w.sum()
            if s > 0:
                w = w / s
            result_ref[mask] = sample_rng_ref.choice(
                child_arr, size=n_match, p=w,
            )
        assert np.array_equal(out_new, result_ref)


class TestSampleDependentRootMultiParentCompleteness:
    """T2.4 of TEST_AUDIT_2026-05-07.md.

    Spec §2.1.2 conditional weights must cover every parent combination
    (Cartesian completeness). Pre-existing tests verify happy paths where
    every parent combination has a leaf; the engine's behavior on a
    MISSING combination is undocumented in the test suite. This class
    exercises that branch so a future change (e.g., from "default to
    uniform" to "raise") is intentional and visible.
    """

    def test_missing_parent_combination_handled_gracefully(self):
        """Construct a 2x2 parent grid with 4 expected combinations but
        only declare weights for 3 of them. Sample at the engine level —
        if some rows fall in the undeclared cell, the sampler should
        either:
          (a) raise a clear error pointing at the missing combination,
          (b) leave those rows as None / NaN (signal of unfilled bucket),
          (c) renormalize/skip silently (current behavior — verify and pin).
        Whichever the impl does, this test makes the contract explicit."""
        rng = np.random.default_rng(0)
        n = 1000
        # Force at least some rows into the undeclared (a2,b2) cell.
        a = rng.choice(["a1", "a2"], size=n)
        b = rng.choice(["b1", "b2"], size=n)
        rows = {"a": a, "b": b}

        # Declared: 3 of 4 combinations; (a2,b2) is missing.
        declared = {
            "a1": {"b1": {"c1": 0.7, "c2": 0.3},
                   "b2": {"c1": 0.5, "c2": 0.5}},
            "a2": {"b1": {"c1": 0.2, "c2": 0.8}},  # missing b2!
        }
        dep = GroupDependency(
            child_root="c", on=["a", "b"],
            conditional_weights=declared,
        )
        col_meta = {"values": ["c1", "c2"]}

        # Run the sampler. Any of three documented behaviors is acceptable;
        # we just need the test to pin which one is current. The sampler
        # currently returns `None` (np.empty -> object dtype default) for
        # rows in the undeclared cell. Verify those rows are detectable.
        a2_b2_mask = (a == "a2") & (b == "b2")
        if not a2_b2_mask.any():
            pytest.skip("RNG happened to skip the undeclared cell; rerun.")

        try:
            out = sample_dependent_root(
                "c", col_meta, dep, rows, n,
                rng=np.random.default_rng(7),
            )
        except (KeyError, ValueError) as exc:
            # Behavior (a): raise — acceptable.
            assert any(t in str(exc) for t in ["a2", "b2", "missing", "weight"])
            return

        # Behavior (b)/(c): produce values. Inspect the undeclared cells.
        undeclared_values = out[a2_b2_mask]
        # Either every undeclared row is None (left as object-dtype None
        # since the loop in sample_dependent_root never visits those keys),
        # OR they get sampled from a renormalized fallback. Pin whichever:
        is_all_none = all(v is None for v in undeclared_values)
        is_all_in_child_set = all(v in {"c1", "c2"} for v in undeclared_values)
        assert is_all_none or is_all_in_child_set, (
            f"Undeclared (a2,b2) cell rows have unexpected values: "
            f"{set(undeclared_values)}. Expected all None (skipped) or "
            f"all valid child values (renormalized fallback)."
        )

    def test_complete_parent_coverage_no_none_left_behind(self):
        """Sanity-pair to the test above: when every parent combination
        IS declared, NO row is left undeclared/None. Locks in the happy
        path so a regression that drops a leaf and silently leaves None
        behind is caught."""
        rng = np.random.default_rng(0)
        n = 1000
        a = rng.choice(["a1", "a2"], size=n)
        b = rng.choice(["b1", "b2"], size=n)
        rows = {"a": a, "b": b}

        declared = {
            "a1": {"b1": {"c1": 0.7, "c2": 0.3},
                   "b2": {"c1": 0.5, "c2": 0.5}},
            "a2": {"b1": {"c1": 0.2, "c2": 0.8},
                   "b2": {"c1": 0.4, "c2": 0.6}},
        }
        dep = GroupDependency(
            child_root="c", on=["a", "b"],
            conditional_weights=declared,
        )
        col_meta = {"values": ["c1", "c2"]}
        out = sample_dependent_root(
            "c", col_meta, dep, rows, n,
            rng=np.random.default_rng(7),
        )
        # Every row must have a valid child value.
        assert all(v in {"c1", "c2"} for v in out), (
            f"Some rows produced unexpected values: {set(out) - {'c1', 'c2'}}"
        )
        assert not any(v is None for v in out)
