"""KS cell-size audit — read-only diagnostic over a generated AGPDS batch.

Quantifies how prevalent small (n<30) per-cell sample sizes are in the Phase 2
KS validator, broken down by complexity tier and by per-measure predictor
dimensionality K. This answers whether tiered ``target_rows`` (set in Phase 1)
keeps the KS validator out of the statistically-unreliable n<30 regime.

The audit recovers every KS cell's sample size by reusing the validator's OWN
cell-enumeration code (``_iter_predictor_cells``) against each scenario's
on-disk ``master_tables/{gen}.csv`` + ``schemas/{gen}_metadata.json``. It does
NOT regex-parse the report detail strings (those cap at 10 cells per
``KS_DETAIL_CELL_CAP`` and never itemize skipped cells).

Two views are produced:

* **Full census** (``min_rows=1``, uncapped): every predictor cell with n>=1.
  This is the honest sparsity picture — % n<30, % n<10, median/quartiles.
* **Validator-faithful** (``min_rows=5``, ``max_cells=100``, CDF-gated): exactly
  reproduces the validator's stage-1 ``tested`` / ``skipped_small`` /
  ``skipped_no_cdf`` counts so the audit can be cross-checked against the
  ``ks_<col>`` detail strings in ``validation/*_report.json``.

This module is read-only: it never mutates pipeline artifacts.

Usage:
    python -m pipeline.phase_2.analysis.ks_cell_size_audit \\
        --batch-dir ./output/agpds/smoke-test-batch-1 \\
        [--tier-map path/to/sidecar.json] [--out report.json] [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from ..validation.statistical import (
    KS_MIN_CELL_SIZE,
    _collect_predictor_cols,
    _compute_cell_params,
    _iter_predictor_cells,
)
from ..engine.distributions import expected_cdf

# Validator stage-1 defaults (must mirror check_stochastic_ks / _iter_predictor_cells).
VALIDATOR_MIN_ROWS = 5
VALIDATOR_MAX_CELLS = 100
SMALL_N_THRESHOLD = KS_MIN_CELL_SIZE  # 30
VERY_SMALL_N_THRESHOLD = 10


# ----------------------------------------------------------------------------
# Per-scenario cell extraction
# ----------------------------------------------------------------------------

def _stochastic_measures(df: pd.DataFrame, columns_meta: dict[str, Any]) -> list[str]:
    """Identify stochastic measure columns exactly as validator._run_l2 does."""
    out = []
    for col_name, col_info in columns_meta.items():
        if not isinstance(col_info, dict):
            continue
        if col_info.get("type") != "measure":
            continue
        if col_info.get("measure_type") != "stochastic":
            continue
        if col_name not in df.columns:
            continue
        out.append(col_name)
    return out


def _exclude_pattern_rows(
    df: pd.DataFrame,
    col_name: str,
    patterns: list[dict[str, Any]] | None,
) -> pd.DataFrame:
    """Replicate check_stochastic_ks pattern-row exclusion for one measure."""
    if not patterns:
        return df
    pattern_mask = pd.Series(False, index=df.index)
    for p in patterns:
        if p.get("col") == col_name:
            try:
                pattern_mask |= df.eval(p["target"])
            except Exception:
                pass
    return df[~pattern_mask]


def _measure_K(col_meta: dict[str, Any], columns_meta: dict[str, Any]) -> int:
    """Number of categorical predictor dimensions for a measure (drives cell_count)."""
    predictor_cols: set[str] = set()
    _collect_predictor_cols(col_meta.get("param_model", {}), columns_meta, predictor_cols)
    return len(predictor_cols)


def audit_scenario(gen_id: str, batch_dir: Path) -> list[dict[str, Any]]:
    """Return one record per (measure, cell) for a single generation.

    Each record: {gen_id, measure, K, n, full_census, validator_tested,
    validator_skipped_small, validator_skipped_no_cdf}. The validator_* flags
    are only meaningful on records produced by the validator-faithful pass; the
    two passes are merged into a per-measure summary downstream.
    """
    csv_path = batch_dir / "master_tables" / f"{gen_id}.csv"
    meta_path = batch_dir / "schemas" / f"{gen_id}_metadata.json"
    if not csv_path.exists() or not meta_path.exists():
        return []

    df = pd.read_csv(csv_path)
    meta = json.loads(meta_path.read_text())
    columns_meta = meta.get("columns", {})
    patterns = meta.get("patterns")

    # Restore categorical dtype fidelity. Declared categorical `values` are
    # strings (e.g. grade_level ['9','10',...]); the CSV round-trip coerces
    # numeric-looking levels to int64, so `df[col] == '9'` would never match
    # and every cell would come back empty. The live df the validator saw held
    # these as strings, so cast declared-categorical columns back to str.
    for col, info in columns_meta.items():
        if isinstance(info, dict) and info.get("type") == "categorical" \
                and col in df.columns:
            df[col] = df[col].astype(str)

    records: list[dict[str, Any]] = []

    for col_name in _stochastic_measures(df, columns_meta):
        col_meta = columns_meta.get(col_name, {})
        K = _measure_K(col_meta, columns_meta)
        family = col_meta.get("family")
        work_df = _exclude_pattern_rows(df, col_name, patterns)

        # --- Full census: every cell with n>=1, uncapped ---
        census_cells = _iter_predictor_cells(
            work_df, col_name, col_meta, columns_meta,
            min_rows=1, max_cells=10 ** 9,
        )
        for predictor_values, cell_df in census_cells:
            n = int(cell_df[col_name].dropna().shape[0])
            records.append({
                "gen_id": gen_id,
                "measure": col_name,
                "K": K,
                "n": n,
                "pass": "census",
            })

        # --- Validator-faithful: reproduce stage-1 tested/skipped counts ---
        v_cells = _iter_predictor_cells(
            work_df, col_name, col_meta, columns_meta,
            min_rows=VALIDATOR_MIN_ROWS, max_cells=VALIDATOR_MAX_CELLS,
        )
        for predictor_values, cell_df in v_cells:
            cell_params = _compute_cell_params(col_meta, predictor_values, columns_meta)
            dist = expected_cdf(family, cell_params) if family is not None else None
            n = int(cell_df[col_name].dropna().shape[0])
            if dist is None:
                status = "skipped_no_cdf"
            elif n < SMALL_N_THRESHOLD:
                status = "skipped_small"
            else:
                status = "tested"
            records.append({
                "gen_id": gen_id,
                "measure": col_name,
                "K": K,
                "n": n,
                "pass": "validator",
                "status": status,
            })

    return records


# ----------------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------------

def _census_stats(ns: list[int]) -> dict[str, Any]:
    if not ns:
        return {"cells": 0}
    total = len(ns)
    lt30 = sum(1 for n in ns if n < SMALL_N_THRESHOLD)
    lt10 = sum(1 for n in ns if n < VERY_SMALL_N_THRESHOLD)
    s = sorted(ns)
    return {
        "cells": total,
        "pct_n_lt_30": round(100 * lt30 / total, 1),
        "pct_n_lt_10": round(100 * lt10 / total, 1),
        "median_n": int(statistics.median(s)),
        "q1_n": int(s[total // 4]),
        "q3_n": int(s[(3 * total) // 4]),
        "min_n": s[0],
        "max_n": s[-1],
    }


def aggregate(
    census_records: list[dict[str, Any]],
    tier_of: dict[str, str],
) -> dict[str, Any]:
    """Aggregate full-census cell records by tier, by K, and by (tier x K)."""
    by_tier: dict[str, list[int]] = defaultdict(list)
    by_K: dict[int, list[int]] = defaultdict(list)
    by_tier_K: dict[tuple[str, int], list[int]] = defaultdict(list)
    overall: list[int] = []

    for r in census_records:
        tier = tier_of.get(r["gen_id"], "unknown")
        by_tier[tier].append(r["n"])
        by_K[r["K"]].append(r["n"])
        by_tier_K[(tier, r["K"])].append(r["n"])
        overall.append(r["n"])

    return {
        "overall": _census_stats(overall),
        "by_tier": {t: _census_stats(ns) for t, ns in sorted(by_tier.items())},
        "by_K": {str(k): _census_stats(ns) for k, ns in sorted(by_K.items())},
        "by_tier_and_K": {
            f"{t}/K={k}": _census_stats(ns)
            for (t, k), ns in sorted(by_tier_K.items())
        },
    }


def validator_faithful_summary(
    validator_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Per-measure tested/skipped_small/skipped_no_cdf counts (for cross-check)."""
    per_measure: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"tested": 0, "skipped_small": 0, "skipped_no_cdf": 0}
    )
    for r in validator_records:
        key = (r["gen_id"], r["measure"])
        per_measure[key][r["status"]] += 1
    return {
        f"{gen}::{meas}": counts
        for (gen, meas), counts in sorted(per_measure.items())
    }


# ----------------------------------------------------------------------------
# Tier map
# ----------------------------------------------------------------------------

def build_tier_map_from_pool(seed: int, pool_path: Path) -> dict[str, str]:
    """Recompute generation_id -> tier for EVERY pool scenario at a given seed.

    Lets the audit join tiers without a sidecar, as long as the batch was
    generated from the cached pool at this seed.
    """
    from pipeline.core.ids import generation_id, format_scenario_id

    tier_of: dict[str, str] = {}
    with pool_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            sid = format_scenario_id(rec["domain_id"], rec["k"])
            tier_of[generation_id(seed, sid)] = rec["complexity_tier"]
    return tier_of


def load_tier_map(path: Path) -> dict[str, str]:
    """Load a sidecar {gen_id: {complexity_tier: ...}} or {gen_id: tier} map."""
    raw = json.loads(path.read_text())
    out: dict[str, str] = {}
    for gen_id, v in raw.items():
        out[gen_id] = v["complexity_tier"] if isinstance(v, dict) else v
    return out


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _discover_gen_ids(batch_dir: Path) -> list[str]:
    mt = batch_dir / "master_tables"
    if not mt.is_dir():
        return []
    return sorted(p.stem for p in mt.glob("*.csv"))


def _print_table(title: str, stats_by_key: dict[str, dict[str, Any]]) -> None:
    print(f"\n{title}")
    print(f"  {'key':<18} {'cells':>7} {'%n<30':>7} {'%n<10':>7} "
          f"{'medN':>6} {'Q1':>5} {'Q3':>5} {'min':>5} {'max':>6}")
    for key, s in stats_by_key.items():
        if not s.get("cells"):
            print(f"  {key:<18} {0:>7}")
            continue
        print(f"  {key:<18} {s['cells']:>7} {s['pct_n_lt_30']:>7} "
              f"{s['pct_n_lt_10']:>7} {s['median_n']:>6} {s['q1_n']:>5} "
              f"{s['q3_n']:>5} {s['min_n']:>5} {s['max_n']:>6}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch-dir", required=True, type=Path,
                    help="Batch dir containing master_tables/, schemas/, validation/")
    ap.add_argument("--tier-map", type=Path, default=None,
                    help="Sidecar JSON mapping generation_id -> tier (or {tier:..}).")
    ap.add_argument("--seed", type=int, default=42,
                    help="Seed to recompute tier map from the pool if no --tier-map.")
    ap.add_argument("--pool-path", type=Path,
                    default=Path("pipeline/phase_1/scenario_pool.jsonl"),
                    help="Scenario pool for seed-based tier recomputation.")
    ap.add_argument("--out", type=Path, default=None,
                    help="Optional path to write the full JSON report.")
    args = ap.parse_args(argv)

    gen_ids = _discover_gen_ids(args.batch_dir)
    if not gen_ids:
        print(f"No master_tables/*.csv found under {args.batch_dir}")
        return 1

    # Tier map: sidecar > seed-recomputed-from-pool > all-unknown.
    if args.tier_map and args.tier_map.exists():
        tier_of = load_tier_map(args.tier_map)
    elif args.pool_path.exists():
        tier_of = build_tier_map_from_pool(args.seed, args.pool_path)
    else:
        tier_of = {}

    all_records: list[dict[str, Any]] = []
    for gen_id in gen_ids:
        all_records.extend(audit_scenario(gen_id, args.batch_dir))

    census = [r for r in all_records if r["pass"] == "census"]
    validator = [r for r in all_records if r["pass"] == "validator"]

    realized_tiers: dict[str, int] = defaultdict(int)
    for gen_id in gen_ids:
        realized_tiers[tier_of.get(gen_id, "unknown")] += 1

    agg = aggregate(census, tier_of)
    vsummary = validator_faithful_summary(validator)

    report = {
        "batch_dir": str(args.batch_dir),
        "scenarios": len(gen_ids),
        "realized_tier_counts": dict(sorted(realized_tiers.items())),
        "census": agg,
        "validator_faithful_per_measure": vsummary,
    }

    # ---- Print human-readable summary ----
    print(f"=== KS cell-size audit: {args.batch_dir} ===")
    print(f"scenarios: {len(gen_ids)}   "
          f"realized tiers: {dict(sorted(realized_tiers.items()))}")
    print(f"total stochastic-measure cells (full census): {agg['overall'].get('cells', 0)}")
    _print_table("By complexity tier:", agg["by_tier"])
    _print_table("By predictor dimensionality K:", agg["by_K"])
    _print_table("By tier x K:", agg["by_tier_and_K"])

    print("\nValidator-faithful stage-1 counts (tested / skipped_small / skipped_no_cdf):")
    for key, c in vsummary.items():
        print(f"  {key:<48} tested={c['tested']:>3} "
              f"small_n={c['skipped_small']:>3} no_cdf={c['skipped_no_cdf']:>3}")

    if args.out:
        args.out.write_text(json.dumps(report, indent=2))
        print(f"\nWrote JSON report -> {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
