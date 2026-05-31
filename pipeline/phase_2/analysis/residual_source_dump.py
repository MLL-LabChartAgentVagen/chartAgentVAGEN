"""Residual-source dump — deterministic, zero-LLM diagnostic for M1.

Answers the open question in
``docs/soft_failure_fix/mechanisms/M1_RESIDUAL_RECONCILIATION.md`` §6/§8:
**Is a structural measure's residual inflation driven by Phase γ pattern
contamination (with P3-8 row-exclusion bypassed), rather than by
multiplicative product variance?** And: once the T9 fix (``patterns=patterns``)
is in place so P3-8 excludes the contaminated rows, does ``residual_std``
fall back to ≈ the declared noise ``sigma``?

The validator (``check_structural_residuals``) recomputes the formula on the
*realized* stored upstream columns, so the product variance is subtracted out
by construction — for a clean measure ``residual == the measure's own additive
noise`` regardless of how large the column's own variance is. The only thing
that can make ``observed != formula(stored columns) + noise`` is a Phase-γ
pattern (or Loop-B reshuffle) mutating a column *after* the downstream measure
already consumed it.

This script proves that mechanism with three controlled experiments on one
synthetic case, and can replay real batch declarations to check the same thing
in the wild. It dumps ``observed`` / ``predicted`` / ``residual`` / pattern-mask
arrays — the comparison the validator's pass/fail verdict hides.

This module is read-only: it never mutates pipeline artifacts.

Usage:
    # Synthetic case (default) — three experiments, prove the mechanism:
    python -m pipeline.phase_2.analysis.residual_source_dump --synthetic

    # Replay a real batch (single declarations file or a batch dir):
    python -m pipeline.phase_2.analysis.residual_source_dump \\
        --declarations ./output/agpds/<batch>            # dir with declarations/
    python -m pipeline.phase_2.analysis.residual_source_dump \\
        --declarations ./output/agpds/<batch>/declarations/<gen_id>.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..engine.generator import run_pipeline
from ..engine.measures import _resolve_effects, _safe_eval_formula
from ..sdk.simulator import FactTableSimulator
from ..serialization import declarations_from_json
from ..validation.statistical import (
    _get_formula_measure_deps,
    check_structural_residuals,
)


# ---------------------------------------------------------------------------
# Core helpers — mirror the validator, but return arrays (not just a Check).
# ---------------------------------------------------------------------------

def residual_arrays(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Recompute (observed, predicted, residual) exactly like the validator.

    Mirrors ``check_structural_residuals`` (statistical.py:525-550): for each
    row, build a context from the realized values of the *other* measure
    columns plus resolved effects, then evaluate the formula. ``residual =
    observed - predicted``. No pattern exclusion here — that is applied
    separately via ``pattern_mask`` so callers can toggle it.
    """
    columns_meta = meta.get("columns", {})
    col_meta = columns_meta.get(col_name, {})
    formula = col_meta["formula"]
    effects_spec = col_meta.get("effects", {})

    predicted = np.empty(len(df), dtype=float)
    for i, (_, row) in enumerate(df.iterrows()):
        context: dict[str, float] = {}
        for other_col, other_info in columns_meta.items():
            if other_info.get("type") == "measure" and other_col != col_name:
                if other_col in df.columns:
                    context[other_col] = float(row[other_col])
        if effects_spec:
            context.update(_resolve_effects(col_meta, dict(row), columns_meta))
        predicted[i] = _safe_eval_formula(formula, context)

    observed = df[col_name].values.astype(float)
    residual = observed - predicted
    return observed, predicted, residual


def pattern_mask(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
    patterns: list[dict[str, Any]] | None,
) -> pd.Series:
    """Reproduce P3-8 (statistical.py:503-516): which rows the validator
    would EXCLUDE from the residual because a pattern targets this column or
    one of its formula's measure dependencies.

    Returns an all-False mask when ``patterns`` is empty — i.e. the T9-bug
    state where the validator received no patterns and excludes nothing.
    """
    mask = pd.Series(False, index=df.index)
    if not patterns:
        return mask
    columns_meta = meta.get("columns", {})
    formula = columns_meta.get(col_name, {}).get("formula", "")
    affected_cols = {col_name} | _get_formula_measure_deps(
        formula, col_name, columns_meta,
    )
    for p in patterns:
        if p.get("col") in affected_cols:
            try:
                mask |= df.eval(p["target"])
            except Exception:  # noqa: BLE001 — mirror validator's silent skip
                pass
    return mask


def _check_residual_std(detail: str) -> float:
    """Pull residual_std=... out of a check_structural_residuals detail."""
    for tok in detail.replace(",", " ").split():
        if tok.startswith("residual_std="):
            return float(tok.split("=", 1)[1])
    raise ValueError(f"no residual_std in detail: {detail!r}")


def analyze_measure(
    df: pd.DataFrame,
    col_name: str,
    meta: dict[str, Any],
    patterns: list[dict[str, Any]] | None,
    *,
    sample_rows: int,
    cross_check: bool = True,
) -> dict[str, Any]:
    """Compute residual stats for one structural measure on one df.

    Returns a dict with the declared sigma, column std, and residual_std both
    WITH P3-8 exclusion (patterns passed) and WITHOUT (patterns=[]), so the
    caller can see how much of the residual is pattern-driven.
    """
    col_meta = meta.get("columns", {}).get(col_name, {})
    sigma = float(col_meta.get("noise", {}).get("sigma", 0.0))

    observed, predicted, residual = residual_arrays(df, col_name, meta)
    mask = pattern_mask(df, col_name, meta, patterns)

    std_all = float(residual.std())
    std_excl = float(residual[~mask.values].std())

    out: dict[str, Any] = {
        "col": col_name,
        "sigma": sigma,
        "column_std": float(observed.std()),
        "n_rows": len(df),
        "n_excluded": int(mask.sum()),
        "residual_std_no_exclusion": std_all,
        "residual_std_with_exclusion": std_excl,
        "ratio_no_exclusion": (abs(std_all - sigma) / sigma) if sigma else float("nan"),
        "ratio_with_exclusion": (abs(std_excl - sigma) / sigma) if sigma else float("nan"),
    }

    # Self-check: our exclusion-aware residual_std must match the validator's
    # own number (guards against this module drifting from statistical.py).
    if cross_check:
        official = check_structural_residuals(df, col_name, meta, patterns=patterns)
        try:
            official_std = _check_residual_std(official.detail)
            # detail prints residual_std at %.4f, so tolerate display rounding.
            assert abs(official_std - std_excl) < 1e-3, (
                f"residual_std drift: ours={std_excl:.6f} "
                f"validator={official_std:.6f} ({official.detail})"
            )
            out["validator_passed"] = official.passed
        except ValueError:
            out["validator_passed"] = official.passed  # deterministic/no-sigma path

    # Sample rows where the residual is largest (most informative).
    order = np.argsort(-np.abs(residual))[:sample_rows]
    out["samples"] = [
        {
            "row": int(i),
            "observed": round(float(observed[i]), 3),
            "predicted": round(float(predicted[i]), 3),
            "residual": round(float(residual[i]), 3),
            "in_pattern_mask": bool(mask.values[i]),
        }
        for i in order
    ]
    return out


def _print_measure_block(title: str, res: dict[str, Any]) -> None:
    print(f"\n--- {title} :: measure `{res['col']}` ---")
    print(
        f"    declared sigma     = {res['sigma']:.4f}\n"
        f"    column std (own)   = {res['column_std']:.4f}   "
        f"(measure's own spread — NOT the residual)\n"
        f"    rows               = {res['n_rows']}, "
        f"pattern-masked = {res['n_excluded']}\n"
        f"    residual_std  (no exclusion / T9-bug) = "
        f"{res['residual_std_no_exclusion']:.4f}   "
        f"ratio={res['ratio_no_exclusion']:.4f}\n"
        f"    residual_std  (P3-8 exclusion / T9-fix) = "
        f"{res['residual_std_with_exclusion']:.4f}   "
        f"ratio={res['ratio_with_exclusion']:.4f}"
    )
    if "validator_passed" in res:
        print(f"    validator verdict (patterns as given) = "
              f"{'PASS' if res['validator_passed'] else 'FAIL'}")
    print("    top-|residual| sample rows "
          "(observed / predicted / residual / in_mask):")
    for s in res["samples"]:
        print(
            f"      row {s['row']:>4}: obs={s['observed']:>12} "
            f"pred={s['predicted']:>12} resid={s['residual']:>12} "
            f"mask={s['in_pattern_mask']}"
        )


# ---------------------------------------------------------------------------
# Synthetic case — mirrors the absentee_count failure (§3) + T9 fixture.
# ---------------------------------------------------------------------------

STRUCTURAL_COL = "enrollment"
DECLARED_SIGMA = 5.0


def _build_synthetic_declarations(rows: int, seed: int) -> dict[str, Any]:
    """A structural product-of-stochastics measure (huge COLUMN variance,
    tiny declared sigma) plus an outlier pattern on it — the canonical M1 shape.
    """
    sim = FactTableSimulator(target_rows=rows, seed=seed)
    sim.add_category("region", values=["N", "S"], weights=[0.5, 0.5], group="geo")
    sim.add_measure(
        "applied", family="gaussian",
        param_model={"mu": {"intercept": 2000.0}, "sigma": {"intercept": 500.0}},
    )
    sim.add_measure(
        "accept_frac", family="gaussian",
        param_model={"mu": {"intercept": 0.30}, "sigma": {"intercept": 0.05}},
    )
    sim.add_measure(
        "yield_rate", family="gaussian",
        param_model={"mu": {"intercept": 0.70}, "sigma": {"intercept": 0.05}},
    )
    # Product of three random variables → large column variance; declared
    # additive noise is deliberately tiny (sigma=5).
    sim.add_measure_structural(
        STRUCTURAL_COL,
        formula="applied * accept_frac * yield_rate",
        effects={},
        noise={"sigma": DECLARED_SIGMA},
    )
    # Outlier pattern on the structural measure itself: spikes `enrollment`
    # for region=='N' AFTER it was computed, so observed != formula(stored).
    sim.inject_pattern(
        "outlier_entity", target="region == 'N'", col=STRUCTURAL_COL,
        params={"z_score": 10.0},
    )
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


def _run_pipeline_from(decls: dict[str, Any], patterns: list[dict[str, Any]]):
    return run_pipeline(
        columns=decls["columns"],
        groups=decls["groups"],
        group_dependencies=decls["group_dependencies"],
        measure_dag=decls["measure_dag"],
        target_rows=decls["target_rows"],
        seed=decls.get("seed", 42),
        patterns=patterns,
        realism_config=None,
        overrides=None,
        orthogonal_pairs=decls.get("orthogonal_pairs", []),
    )


def run_synthetic(rows: int, seed: int, sample_rows: int) -> None:
    print("=" * 74)
    print("SYNTHETIC CASE — structural product measure + outlier pattern")
    print(f"  formula: {STRUCTURAL_COL} = applied * accept_frac * yield_rate")
    print(f"  declared noise sigma = {DECLARED_SIGMA}")
    print(f"  pattern: outlier_entity on `{STRUCTURAL_COL}` where region=='N'")
    print(f"  rows={rows} seed={seed}")
    print("=" * 74)

    decls = _build_synthetic_declarations(rows, seed)
    patterns = decls["patterns"]

    # Experiment ① — no pattern at all.
    df1, meta1 = _run_pipeline_from(decls, patterns=[])
    res1 = analyze_measure(df1, STRUCTURAL_COL, meta1, patterns=[],
                           sample_rows=sample_rows)
    _print_measure_block("EXP ① no pattern", res1)
    print("    => 预期 residual_std ≈ σ：乘积方差只进 column std，不进 residual。")

    # Experiments ② / ③ — same patterned df, toggle P3-8 exclusion.
    df2, meta2 = _run_pipeline_from(decls, patterns=patterns)
    res2 = analyze_measure(df2, STRUCTURAL_COL, meta2, patterns=patterns,
                           sample_rows=sample_rows)
    _print_measure_block("EXP ② pattern + P3-8 ON (T9 fix)", res2)
    print("    => 预期 residual_std ≈ σ：pattern 行被排除，residual 干净。")

    res3 = analyze_measure(df2, STRUCTURAL_COL, meta2, patterns=[],
                           sample_rows=sample_rows)
    _print_measure_block("EXP ③ pattern + P3-8 OFF (simulated T9 bug)", res3)
    print("    => 预期 residual_std ≫ σ：pattern 行被计入，复现 66× 机制（σ 无关）。")

    # Verdict.
    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)
    r1 = res1["residual_std_no_exclusion"]
    r2 = res2["residual_std_with_exclusion"]
    r3 = res3["residual_std_no_exclusion"]
    print(f"  ① no pattern             residual_std = {r1:8.3f}  (σ={DECLARED_SIGMA})")
    print(f"  ② pattern + P3-8 ON      residual_std = {r2:8.3f}")
    print(f"  ③ pattern + P3-8 OFF     residual_std = {r3:8.3f}")
    print(f"  enrollment COLUMN std    = {res1['column_std']:8.3f}  "
          f"(≫ residual — product variance lives here, not in residual)")
    clean = r1 < 3 * DECLARED_SIGMA and r2 < 3 * DECLARED_SIGMA
    inflated = r3 > 5 * DECLARED_SIGMA
    if clean and inflated:
        print("\n  ✓ 机制确认：residual 膨胀完全由 pattern 行驱动（σ 无关），"
              "T9 修复（P3-8 排除）让 residual 回到 ≈ σ；乘积方差从不进 residual。")
    else:
        print("\n  ⚠ 结果不符合预期，需人工核查上面的实验输出。")


# ---------------------------------------------------------------------------
# Real-batch replay mode.
# ---------------------------------------------------------------------------

def _iter_declaration_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    decl_dir = path / "declarations" if (path / "declarations").is_dir() else path
    return sorted(decl_dir.glob("*.json"))


def run_declarations(path_str: str, sample_rows: int) -> None:
    path = Path(path_str)
    files = _iter_declaration_files(path)
    if not files:
        print(f"No declarations/*.json found under {path}")
        return
    print("=" * 74)
    print(f"DECLARATIONS REPLAY — {len(files)} file(s) under {path}")
    print("  per structural measure: residual_std with P3-8 ON vs OFF")
    print("=" * 74)

    for f in files:
        with open(f, encoding="utf-8") as fh:
            decls = declarations_from_json(json.load(fh))
        patterns = decls.get("patterns", []) or []
        try:
            df, meta = _run_pipeline_from(decls, patterns=patterns)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[{f.name}] run_pipeline failed: {exc}")
            continue

        structural = [
            c for c, m in meta.get("columns", {}).items()
            if m.get("type") == "measure" and m.get("measure_type") == "structural"
            and c in df.columns
        ]
        print(f"\n### {f.name}  ({len(structural)} structural measure(s), "
              f"{len(patterns)} pattern(s))")
        if not structural:
            print("    (no structural measures)")
            continue
        for col in structural:
            res = analyze_measure(df, col, meta, patterns=patterns,
                                  sample_rows=sample_rows)
            driven = (
                res["residual_std_no_exclusion"]
                > 1.5 * max(res["residual_std_with_exclusion"], 1e-9)
            )
            tag = "  <-- pattern-driven inflation" if driven else ""
            print(
                f"    {col:<28} σ={res['sigma']:<10.4f} "
                f"resid_std P3-8 ON={res['residual_std_with_exclusion']:<10.3f} "
                f"OFF={res['residual_std_no_exclusion']:<10.3f} "
                f"masked={res['n_excluded']}{tag}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic residual-source dump for M1 (see module docstring).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--synthetic", action="store_true",
                      help="Run the built-in synthetic 3-experiment case (default).")
    mode.add_argument("--declarations", metavar="PATH",
                      help="A declarations/{gen}.json file or a batch dir to replay.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rows", type=int, default=400,
                        help="Synthetic row count (default 400).")
    parser.add_argument("--sample-rows", type=int, default=8,
                        help="How many top-|residual| sample rows to print.")
    args = parser.parse_args()

    if args.declarations:
        run_declarations(args.declarations, args.sample_rows)
    else:
        run_synthetic(args.rows, args.seed, args.sample_rows)


if __name__ == "__main__":
    main()
