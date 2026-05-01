"""Tests for DS-4 multi-parent ``sample_dependent_root`` engine sampling.

Covers:
- 2-parent sampling reproduces declared conditional within tolerance.
- 3-parent sampling reproduces declared conditional.
- Single-parent fast path produces byte-identical RNG output to v1
  (regression guard so callers depending on a fixed seed are stable).
"""
from __future__ import annotations

import numpy as np

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
