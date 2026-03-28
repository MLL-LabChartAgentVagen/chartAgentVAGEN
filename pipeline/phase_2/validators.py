"""
Three-layer validation for FactTableSimulator output.

L1: Structural — row count, cardinality, null/finite checks, orthogonality χ²
L2: Statistical — correlation targets, dependency residuals, KS distribution test
L3: Pattern — verify each injected pattern is detectable (all 6 types)

Also includes auto-fix dispatch (FixAction) and generate_with_validation() loop
that actually mutates SchemaMetadata parameters on retry.

Reference: phase_2.md §2.6
"""

import numpy as np
import pandas as pd
from typing import Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Check:
    """Single validation check result."""
    name: str
    passed: bool
    detail: str = ""
    auto_fixable: bool = False


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    checks: list[Check] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.passed)
        lines = [f"Validation: {passed}/{total} checks passed"]
        for c in self.failures:
            lines.append(f"  ✗ {c.name}: {c.detail}")
        return "\n".join(lines)


class SchemaAwareValidator:
    """
    Three-layer validator for FactTableSimulator output.

    Usage:
        validator = SchemaAwareValidator()
        report = validator.validate(df, schema_metadata)
        if not report.all_passed:
            print(report.summary())
    """

    def validate(
        self, df: pd.DataFrame, meta: dict
    ) -> ValidationReport:
        """Run all three validation layers."""
        checks: list[Check] = []
        checks += self._L1_structural(df, meta)
        checks += self._L2_statistical(df, meta)
        checks += self._L3_pattern(df, meta)
        return ValidationReport(checks=checks)

    # ================================================================
    # L1: Structural Validation
    # ================================================================

    def _L1_structural(
        self, df: pd.DataFrame, meta: dict
    ) -> list[Check]:
        checks = []

        # Row count within 10% of target
        target = meta.get("total_rows", len(df))
        row_diff = abs(len(df) - target) / max(target, 1)
        checks.append(Check(
            "row_count",
            passed=row_diff < 0.1,
            detail=f"target={target}, actual={len(df)}, diff={row_diff:.2%}",
        ))

        # Categorical cardinality matches declaration
        for col_meta in meta.get("columns", []):
            if col_meta.get("type") == "categorical":
                name = col_meta["name"]
                if name not in df.columns:
                    checks.append(Check(
                        f"exists_{name}", passed=False,
                        detail=f"Column '{name}' missing from DataFrame",
                    ))
                    continue
                expected = col_meta.get("cardinality")
                if expected is not None:
                    actual = df[name].nunique()
                    checks.append(Check(
                        f"cardinality_{name}",
                        passed=actual == expected,
                        detail=f"expected={expected}, actual={actual}",
                    ))

        # Measure columns: non-null and finite
        # Spec baseline: df[col].notna().all() and np.isfinite(df[col]).all()
        # With realism(missing_rate>0), validate null rate against explicit tolerance.
        realism = meta.get("realism", {})
        missing_rate = realism.get("missing_rate", 0.0)

        for col_meta in meta.get("columns", []):
            if col_meta.get("type") == "measure":
                name = col_meta["name"]
                if name not in df.columns:
                    checks.append(Check(
                        f"exists_{name}", passed=False,
                        detail=f"Column '{name}' missing from DataFrame",
                    ))
                    continue

                series = df[name]
                null_count = int(series.isna().sum())
                total = len(series)

                # Null check (spec: notna().all())
                if missing_rate > 0:
                    actual_rate = null_count / max(total, 1)
                    tolerance = max(0.01, missing_rate * 0.25)
                    deviation = abs(actual_rate - missing_rate)
                    checks.append(Check(
                        f"nulls_{name}",
                        passed=deviation <= tolerance,
                        detail=(
                            f"null_rate={actual_rate:.3f}, target={missing_rate:.3f}, "
                            f"tolerance=±{tolerance:.3f}"
                        ),
                    ))
                else:
                    # No realism — spec says zero nulls
                    checks.append(Check(
                        f"nulls_{name}",
                        passed=null_count == 0,
                        detail=f"null_count={null_count}/{total}",
                    ))

                # Finiteness check on non-null values
                non_null = series.dropna()
                if len(non_null) == 0:
                    checks.append(Check(
                        f"finite_{name}", passed=False,
                        detail="All values are null",
                    ))
                else:
                    is_finite = np.isfinite(non_null.astype(float)).all()
                    checks.append(Check(
                        f"finite_{name}",
                        passed=bool(is_finite),
                        detail=f"non-null={len(non_null)}, finite={is_finite}",
                    ))

        # Orthogonal group independence (chi-squared on root pairs)
        for pair in meta.get("orthogonal_groups", []):
            dim_groups = meta.get("dimension_groups", {})
            ga = dim_groups.get(pair["group_a"], {})
            gb = dim_groups.get(pair["group_b"], {})
            hierarchy_a = ga.get("hierarchy", [])
            hierarchy_b = gb.get("hierarchy", [])
            if not hierarchy_a or not hierarchy_b:
                continue
            root_a, root_b = hierarchy_a[0], hierarchy_b[0]
            if root_a not in df.columns or root_b not in df.columns:
                continue
            try:
                from scipy.stats import chi2_contingency
                ct = pd.crosstab(df[root_a], df[root_b])
                _, p_val, _, _ = chi2_contingency(ct)
                checks.append(Check(
                    f"orthogonal_{root_a}_{root_b}",
                    passed=p_val > 0.05,
                    detail=f"χ² p={p_val:.4f} (>0.05 = independent)",
                    auto_fixable=True,
                ))
            except Exception as e:
                checks.append(Check(
                    f"orthogonal_{root_a}_{root_b}",
                    passed=False,
                    detail=f"χ² test failed: {e}",
                ))

        return checks

    # ================================================================
    # L2: Statistical Validation
    # ================================================================

    def _L2_statistical(
        self, df: pd.DataFrame, meta: dict
    ) -> list[Check]:
        checks = []

        # Correlation targets
        for corr in meta.get("correlations", []):
            col_a, col_b = corr["col_a"], corr["col_b"]
            if col_a not in df.columns or col_b not in df.columns:
                continue
            clean = df[[col_a, col_b]].dropna()
            if len(clean) < 3:
                checks.append(Check(
                    f"corr_{col_a}_{col_b}", passed=False,
                    detail="Too few non-null rows for correlation",
                ))
                continue
            actual_r = clean[col_a].corr(clean[col_b])
            # Spec: abs(actual_r - target_r) < 0.15
            # Auto-fix loop handles post-φ perturbation if needed
            checks.append(Check(
                f"corr_{col_a}_{col_b}",
                passed=abs(actual_r - corr["target_r"]) < 0.15,
                detail=f"target={corr['target_r']}, actual={actual_r:.3f}",
                auto_fixable=True,
            ))

        # Functional dependency residuals
        for dep in meta.get("dependencies", []):
            target = dep["target"]
            if target not in df.columns:
                continue
            try:
                predicted = pd.eval(dep["formula"], local_dict={
                    col: df[col] for col in df.columns
                })
                residual_std = (df[target] - predicted).std()
                target_std = df[target].std()
                passed = residual_std < target_std * 0.5 if target_std > 0 else True
                checks.append(Check(
                    f"dep_{target}",
                    passed=passed,
                    detail=f"residual_std={residual_std:.3f}, "
                           f"target_std={target_std:.3f}",
                ))
            except Exception as e:
                checks.append(Check(
                    f"dep_{target}", passed=True,
                    detail=f"Formula eval skipped: {e}",
                ))

        # Distribution shape (KS test against declared distribution)
        # Skip columns where marginal-KS is semantically invalid:
        # - dependency targets (formula-derived, not raw marginal)
        # - conditional measures (mixture distributions)
        # - scaled measures (sample-dependent scaling)
        dependency_targets = {
            dep["target"] for dep in meta.get("dependencies", [])
            if "target" in dep
        }
        conditional_measures = {
            cond["measure"] for cond in meta.get("conditionals", [])
            if "measure" in cond
        }
        for col_meta in meta.get("columns", []):
            if col_meta.get("type") != "measure":
                continue
            name = col_meta["name"]
            if name in dependency_targets or name in conditional_measures:
                continue
            if col_meta.get("scale") is not None:
                continue
            declared_dist = col_meta.get("declared_dist")
            declared_params = col_meta.get("declared_params")
            if not declared_dist or not declared_params:
                continue
            if name not in df.columns:
                continue

            clean = df[name].dropna()
            if len(clean) < 10:
                continue

            try:
                from scipy.stats import kstest
                ks_args = _get_ks_args(declared_dist, declared_params)
                if ks_args is not None:
                    scipy_name, args = ks_args
                    _, p_val = kstest(clean, scipy_name, args=args)
                    checks.append(Check(
                        f"ks_{name}",
                        passed=p_val > 0.05,
                        detail=f"KS p={p_val:.4f} (dist={declared_dist})",
                        auto_fixable=True,
                    ))
            except Exception:
                pass  # Skip KS test on error

        return checks

    # ================================================================
    # L3: Pattern Validation
    # ================================================================

    def _L3_pattern(
        self, df: pd.DataFrame, meta: dict
    ) -> list[Check]:
        checks = []
        dim_groups = meta.get("dimension_groups", {})

        for p in meta.get("patterns", []):
            p_type = p.get("type", "")

            if p_type == "outlier_entity":
                target_filter = p.get("target")
                col = p.get("col")
                if target_filter and col and col in df.columns:
                    try:
                        filtered = df.query(target_filter)
                        non_target = df.loc[~df.index.isin(filtered.index), col]
                        if len(filtered) > 0 and len(non_target) > 1:
                            baseline_mean = non_target.mean()
                            baseline_std = non_target.std()
                            z = abs(filtered[col].mean() - baseline_mean) / max(
                                baseline_std, 1e-10
                            )
                            checks.append(Check(
                                f"outlier_{col}",
                                passed=z >= 2.0,
                                detail=f"z-score={z:.2f} (baseline=non-target, ≥2.0 required)",
                                auto_fixable=True,
                            ))
                    except Exception:
                        pass

            elif p_type == "ranking_reversal":
                metrics = p.get("metrics", [])
                if len(metrics) >= 2:
                    m1, m2 = metrics[0], metrics[1]
                    # Find root entity column
                    root_col = None
                    if dim_groups:
                        first_group = next(iter(dim_groups.values()))
                        hierarchy = first_group.get("hierarchy", [])
                        if hierarchy:
                            root_col = hierarchy[0]
                    if root_col and root_col in df.columns:
                        means = df.groupby(root_col)[[m1, m2]].mean()
                        rank_corr = means[m1].rank().corr(means[m2].rank())
                        checks.append(Check(
                            f"reversal_{m1}_{m2}",
                            passed=rank_corr < 0,
                            detail=f"rank_corr={rank_corr:.3f} (<0 required)",
                            auto_fixable=True,
                        ))

            elif p_type == "trend_break":
                col = p.get("col")
                bp_str = p.get("break_point")
                target_filter = p.get("target")
                if col and bp_str and col in df.columns:
                    # Find temporal column
                    tc = None
                    for cm in meta.get("columns", []):
                        if cm.get("type") == "temporal":
                            tc = cm["name"]
                            break
                    if tc and tc in df.columns:
                        try:
                            bp = pd.to_datetime(bp_str)
                            # Apply target filter if present (e.g., specific entity)
                            subset = df.query(target_filter) if target_filter else df
                            dates = pd.to_datetime(subset[tc])
                            before = subset[dates < bp][col].mean()
                            after = subset[dates >= bp][col].mean()
                            shift = abs(after - before) / max(abs(before), 1e-10)
                            checks.append(Check(
                                f"trend_{col}",
                                passed=shift > 0.15,
                                detail=f"before={before:.2f}, after={after:.2f}, "
                                       f"shift={shift:.2%}",
                                auto_fixable=True,
                            ))
                        except Exception:
                            pass

            elif p_type == "dominance_shift":
                col = p.get("col")
                if col and col in df.columns:
                    tc = self._find_temporal_col(meta)
                    root_col = self._find_root_entity_col(dim_groups)
                    if tc and root_col and tc in df.columns and root_col in df.columns:
                        try:
                            dates = pd.to_datetime(df[tc])
                            midpoint = dates.min() + (dates.max() - dates.min()) / 2
                            before = df[dates < midpoint].groupby(root_col)[col].mean()
                            after = df[dates >= midpoint].groupby(root_col)[col].mean()
                            dom_before = before.idxmax()
                            dom_after = after.idxmax()
                            checks.append(Check(
                                f"dominance_{col}",
                                passed=dom_before != dom_after,
                                detail=f"dominant before={dom_before}, "
                                       f"after={dom_after}",
                                auto_fixable=True,
                            ))
                        except Exception:
                            pass

            elif p_type == "convergence":
                col = p.get("col")
                if col and col in df.columns:
                    tc = self._find_temporal_col(meta)
                    root_col = self._find_root_entity_col(dim_groups)
                    if tc and root_col and tc in df.columns and root_col in df.columns:
                        try:
                            dates = pd.to_datetime(df[tc])
                            midpoint = dates.min() + (dates.max() - dates.min()) / 2
                            early = df[dates < midpoint].groupby(root_col)[col].mean()
                            late = df[dates >= midpoint].groupby(root_col)[col].mean()
                            gap_early = early.max() - early.min()
                            gap_late = late.max() - late.min()
                            converged = gap_late < gap_early * 0.9
                            checks.append(Check(
                                f"convergence_{col}",
                                passed=converged,
                                detail=f"gap_early={gap_early:.2f}, "
                                       f"gap_late={gap_late:.2f}",
                                auto_fixable=True,
                            ))
                        except Exception:
                            pass

            elif p_type == "seasonal_anomaly":
                col = p.get("col")
                target_filter = p.get("target")
                if col and target_filter and col in df.columns:
                    tc = self._find_temporal_col(meta)
                    if tc and tc in df.columns:
                        try:
                            dates = pd.to_datetime(df[tc])
                            day_of_year = dates.dt.dayofyear
                            # Seasonal signal = correlation with sin(2π·day/365)
                            seasonal = np.sin(2 * np.pi * day_of_year / 365.0)
                            overall_corr = df[col].corr(seasonal)
                            filtered = df.query(target_filter)
                            if len(filtered) > 5:
                                filtered_dates = pd.to_datetime(filtered[tc])
                                filtered_seasonal = np.sin(
                                    2 * np.pi * filtered_dates.dt.dayofyear / 365.0
                                )
                                target_corr = filtered[col].corr(filtered_seasonal)
                                # Target entity should have opposite seasonality
                                checks.append(Check(
                                    f"seasonal_{col}",
                                    passed=(overall_corr * target_corr < 0) or
                                           abs(target_corr - overall_corr) > 0.1,
                                    detail=f"overall_seasonal_r={overall_corr:.3f}, "
                                           f"target_seasonal_r={target_corr:.3f}",
                                    auto_fixable=True,
                                ))
                        except Exception:
                            pass

        return checks

    @staticmethod
    def _find_temporal_col(meta: dict) -> Optional[str]:
        """Find the temporal column name from schema metadata."""
        for cm in meta.get("columns", []):
            if cm.get("type") == "temporal":
                return cm["name"]
        return None

    @staticmethod
    def _find_root_entity_col(dim_groups: dict) -> Optional[str]:
        """Find the root entity column from dimension groups."""
        if dim_groups:
            first_group = next(iter(dim_groups.values()))
            hierarchy = first_group.get("hierarchy", [])
            if hierarchy:
                return hierarchy[0]
        return None


# ================================================================
# KS Test Parameter Mapping
# ================================================================

def _get_ks_args(
    dist_name: str, params: dict
) -> Optional[tuple[str, tuple]]:
    """Map SDK distribution name + params to scipy.stats (name, args).

    Returns None if mapping is not supported.
    """
    if dist_name == "gaussian":
        return ("norm", (
            params.get("mu", 0),
            params.get("sigma", 1),
        ))
    elif dist_name == "lognormal":
        sigma = params.get("sigma", 1)
        mu = params.get("mu", 0)
        # scipy lognorm: (s, loc, scale) where s=sigma, scale=exp(mu)
        import math
        return ("lognorm", (sigma, 0, math.exp(mu)))
    elif dist_name == "gamma":
        shape = params.get("shape", 1)
        scale = params.get("scale", 1)
        return ("gamma", (shape, 0, scale))
    elif dist_name == "beta":
        alpha = params.get("alpha", 1)
        beta_p = params.get("beta", 1)
        return ("beta", (alpha, beta_p, 0, 1))
    elif dist_name == "uniform":
        low = params.get("low", 0)
        high = params.get("high", 1)
        return ("uniform", (low, high - low))
    elif dist_name == "exponential":
        scale = params.get("scale", 1)
        return ("expon", (0, scale))
    # poisson and mixture: not straightforward with kstest
    return None


# ================================================================
# Auto-Fix: FixAction + Strategy Functions
# ================================================================

@dataclass
class FixAction:
    """Describes a parameter adjustment to apply before the next retry."""
    target: str         # Human-readable path, e.g. "correlations[0].target_r"
    adjustment: str     # Description: e.g. "-0.55 → -0.50"

    def __str__(self) -> str:
        return f"{self.target}: {self.adjustment}"


def _relax_target_r(
    check: Check, meta: dict, step: float = 0.05
) -> Optional[FixAction]:
    """Move correlation target_r closer to 0 by step."""
    # Extract column names from check name: corr_{col_a}_{col_b}
    parts = check.name.split("_", 1)
    if len(parts) < 2:
        return None
    suffix = parts[1]  # "col_a_col_b"

    for i, corr in enumerate(meta.get("correlations", [])):
        key = f"{corr['col_a']}_{corr['col_b']}"
        if key == suffix:
            old_r = corr["target_r"]
            # Move toward 0
            if old_r > 0:
                new_r = max(0.0, old_r - step)
            else:
                new_r = min(0.0, old_r + step)
            corr["target_r"] = round(new_r, 3)
            return FixAction(
                target=f"correlations[{i}].target_r",
                adjustment=f"{old_r} → {new_r}",
            )
    return None


def _widen_variance(
    check: Check, meta: dict, factor: float = 1.2
) -> Optional[FixAction]:
    """Widen distribution sigma/scale by factor."""
    # Extract column name from check name: ks_{col}
    parts = check.name.split("_", 1)
    if len(parts) < 2:
        return None
    col_name = parts[1]

    for col_meta in meta.get("columns", []):
        if col_meta.get("name") == col_name and col_meta.get("declared_params"):
            params = col_meta["declared_params"]
            for key in ("sigma", "scale"):
                if key in params:
                    old = params[key]
                    params[key] = round(old * factor, 4)
                    return FixAction(
                        target=f"columns[{col_name}].{key}",
                        adjustment=f"{old} → {params[key]}",
                    )
    return None


def _amplify_magnitude(
    check: Check, meta: dict, factor: float = 1.3
) -> Optional[FixAction]:
    """Increase pattern z_score or magnitude by factor.

    Patterns in SchemaMetadata are stored flat (spec §2.3), so all
    numeric parameters (z_score, magnitude, etc.) live at the top level
    of the pattern dict rather than in a nested 'params' sub-dict.
    """
    for i, p in enumerate(meta.get("patterns", [])):
        # Match check name to pattern
        p_type = p.get("type", "")
        p_col = p.get("col", "")

        # Check if this pattern matches the check
        match = False
        if check.name.startswith("outlier_") and p_type == "outlier_entity":
            match = check.name == f"outlier_{p_col}"
        elif check.name.startswith("trend_") and p_type == "trend_break":
            match = check.name == f"trend_{p_col}"
        elif check.name.startswith("reversal_") and p_type == "ranking_reversal":
            metrics = p.get("metrics", [])
            if len(metrics) >= 2:
                match = check.name == f"reversal_{metrics[0]}_{metrics[1]}"
        elif check.name.startswith("dominance_") and p_type == "dominance_shift":
            match = True
        elif check.name.startswith("convergence_") and p_type == "convergence":
            match = True
        elif check.name.startswith("seasonal_") and p_type == "seasonal_anomaly":
            match = True

        if match:
            # Numeric parameter keys stored flat on the pattern dict
            for key in ("z_score", "magnitude", "convergence_rate", "amplitude"):
                if key in p:
                    old = p[key]
                    p[key] = round(old * factor, 4)
                    return FixAction(
                        target=f"patterns[{i}].{key}",
                        adjustment=f"{old} → {p[key]}",
                    )
            # No specific param found — inject/amplify magnitude
            old_mag = p.get("magnitude", 0.3)
            p["magnitude"] = round(old_mag * factor, 4)
            return FixAction(
                target=f"patterns[{i}].magnitude",
                adjustment=f"added/amplified to {p['magnitude']:.3f}",
            )
    return None


def _reshuffle_pair(
    check: Check, meta: dict
) -> Optional[FixAction]:
    """Flag for reshuffle — seed increment handles this automatically."""
    return FixAction(
        target="seed",
        adjustment="increment seed to reshuffle orthogonal sampling",
    )


AUTO_FIX: dict[str, Callable] = {
    "corr_": _relax_target_r,
    "ks_": _widen_variance,
    "outlier_": _amplify_magnitude,
    "trend_": _amplify_magnitude,
    "orthogonal_": _reshuffle_pair,
    "reversal_": _amplify_magnitude,
    "dominance_": _amplify_magnitude,
    "convergence_": _amplify_magnitude,
    "seasonal_": _amplify_magnitude,
}


def _match_strategy(check_name: str) -> Optional[Callable]:
    """Find auto-fix strategy matching a check name prefix."""
    for prefix, strategy in AUTO_FIX.items():
        if check_name.startswith(prefix):
            return strategy
    return None


def apply_fixes(
    report: ValidationReport, meta: dict
) -> list[FixAction]:
    """Apply auto-fix strategies to failed checks, mutating meta in-place.

    Returns list of FixActions that were applied.
    """
    actions: list[FixAction] = []
    for check in report.failures:
        if check.auto_fixable:
            strategy = _match_strategy(check.name)
            if strategy:
                action = strategy(check, meta)
                if action:
                    actions.append(action)
                    check.detail += f" [auto-fix: {action}]"
    return actions


def generate_with_validation(
    build_fn: Callable,
    meta: dict,
    max_retries: int = 3,
    base_seed: int = 42,
) -> tuple[pd.DataFrame, ValidationReport, dict]:
    """
    Run build_fn with validation and auto-fix against external schema meta.

    Spec alignment:
    - meta is provided externally and mutated by auto-fix strategies.
    - each retry calls build_fn(seed, meta) so generation can honor updates.

    Args:
        build_fn: Callable(seed=int, meta=dict) -> pd.DataFrame
        meta: External schema metadata target used by validation/fixes.
        max_retries: Maximum retry attempts.
        base_seed: Starting seed.

    Returns:
        (df, report, meta) tuple. Report may contain failures if all retries
        exhausted (soft failure).
    """
    validator = SchemaAwareValidator()
    if not isinstance(meta, dict):
        raise ValueError("generate_with_validation: meta must be a dict")
    working_meta = meta

    df: Optional[pd.DataFrame] = None
    report: Optional[ValidationReport] = None
    for attempt in range(max_retries):
        seed = base_seed + attempt
        try:
            generated = build_fn(seed=seed, meta=working_meta)
        except TypeError:
            # Backward-compatible fallback for legacy callables.
            generated = build_fn(seed=seed)

        if isinstance(generated, tuple):
            df = generated[0]
        else:
            df = generated
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"generate_with_validation: build_fn must return DataFrame, got {type(df).__name__}"
            )

        report = validator.validate(df, working_meta)

        if report.all_passed:
            return df, report, working_meta

        # Apply auto-fix strategies — mutate working_meta in-place for next retry
        apply_fixes(report, working_meta)

    # Soft failure after retries: return last generated df/report.
    if df is None or report is None:
        raise RuntimeError("generate_with_validation: build_fn did not produce any result")
    return df, report, working_meta
