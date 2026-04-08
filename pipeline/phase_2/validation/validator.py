"""
SchemaAwareValidator — orchestration class for three-layer validation.

Composes L1 (structural), L2 (statistical), and L3 (pattern) checks
into a single validate() method that returns a ValidationReport.

Implements: §2.9 orchestrator
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from ..types import Check, ValidationReport
from . import structural as _l1
from . import statistical as _l2
from . import pattern_checks as _l3

logger = logging.getLogger(__name__)


class SchemaAwareValidator:
    """Orchestrates three-layer validation for generated DataFrames.

    [Target Architecture — M5]

    Usage:
        validator = SchemaAwareValidator(meta)
        report = validator.validate(df)
        if not report.all_passed:
            for check in report.failures:
                print(f"FAILED: {check.name}: {check.detail}")

    Attributes:
        meta: Schema metadata dict (immutable reference).
    """

    def __init__(self, meta: dict[str, Any]) -> None:
        """Initialize with schema metadata.

        Args:
            meta: Schema metadata dict from build_schema_metadata().
        """
        self.meta = meta

    def validate(
        self,
        df: pd.DataFrame,
        patterns: list[dict[str, Any]] | None = None,
    ) -> ValidationReport:
        """Run all validation layers and return a combined report.

        Args:
            df: Generated DataFrame to validate.
            patterns: Optional pattern specs for L3 checks.

        Returns:
            ValidationReport with all Check results.
        """
        report = ValidationReport()

        # ===== L1: Structural Checks =====
        l1_checks = self._run_l1(df)
        report.add_checks(l1_checks)

        # ===== L2: Statistical Checks =====
        l2_checks = self._run_l2(df, patterns)
        report.add_checks(l2_checks)

        # ===== L3: Pattern Checks =====
        if patterns:
            l3_checks = self._run_l3(df, patterns)
            report.add_checks(l3_checks)

        logger.debug(
            "SchemaAwareValidator.validate: %d checks, %d failures.",
            len(report.checks),
            len(report.failures),
        )

        return report

    def _run_l2(
        self,
        df: pd.DataFrame,
        patterns: list[dict[str, Any]] | None = None,
    ) -> list[Check]:
        """Execute L2 statistical checks for measure columns and group deps.

        [P3-15, P3-16, M5 SPEC_READY #9]

        Dispatches to check_structural_residuals or check_stochastic_ks
        based on measure_type. Also runs check_group_dependency_transitions
        for declared group dependencies. Silently skips columns where
        metadata is insufficient.

        Args:
            df: Generated DataFrame.
            patterns: Optional pattern specs for residual exclusion (P3-8).

        Returns:
            List of Check results from L2 layer.
        """
        checks: list[Check] = []
        columns_meta = self.meta.get("columns")
        if not columns_meta or not isinstance(columns_meta, dict):
            return checks

        for col_name, col_info in columns_meta.items():
            if col_info.get("type") != "measure":
                continue
            if col_name not in df.columns:
                continue

            measure_type = col_info.get("measure_type", "")

            try:
                if measure_type == "structural":
                    checks.append(
                        _l2.check_structural_residuals(
                            df, col_name, self.meta, patterns=patterns,
                        )
                    )
                elif measure_type == "stochastic":
                    checks.extend(
                        _l2.check_stochastic_ks(df, col_name, self.meta, patterns=patterns)
                    )
            except Exception as exc:
                checks.append(Check(
                    name=f"l2_{col_name}",
                    passed=False,
                    detail=f"L2 check error: {exc}",
                ))

        # Group dependency conditional weight checks (M5 SPEC_READY #9)
        try:
            checks.extend(
                _l2.check_group_dependency_transitions(df, self.meta)
            )
        except Exception as exc:
            checks.append(Check(
                name="group_dep_error",
                passed=False,
                detail=f"Group dependency check error: {exc}",
            ))

        return checks

    def _run_l1(self, df: pd.DataFrame) -> list[Check]:
        """Execute all L1 structural checks.

        Returns:
            List of Check results from L1 layer.
        """
        checks: list[Check] = []

        # Row count check
        checks.append(_l1.check_row_count(df, self.meta))

        # Categorical cardinality checks
        checks.extend(_l1.check_categorical_cardinality(df, self.meta))

        # Orthogonal independence checks
        checks.extend(_l1.check_orthogonal_independence(df, self.meta))

        # Measure DAG acyclicity
        checks.append(_l1.check_measure_dag_acyclic(self.meta))

        # Marginal weight checks (P0-1)
        checks.extend(_l1.check_marginal_weights(df, self.meta))

        # Measure finiteness checks (P0-1)
        checks.extend(_l1.check_measure_finiteness(df, self.meta))

        return checks

    def _run_l3(
        self,
        df: pd.DataFrame,
        patterns: list[dict[str, Any]],
    ) -> list[Check]:
        """Execute L3 pattern validation checks.

        Args:
            df: Generated DataFrame.
            patterns: Pattern spec list.

        Returns:
            List of Check results from L3 layer.
        """
        checks: list[Check] = []

        for pattern in patterns:
            pattern_type = pattern.get("type", "")

            try:
                if pattern_type == "outlier_entity":
                    checks.append(_l3.check_outlier_entity(df, pattern))
                elif pattern_type == "trend_break":
                    checks.append(_l3.check_trend_break(df, pattern, self.meta))
                elif pattern_type == "dominance_shift":
                    checks.append(_l3.check_dominance_shift(df, pattern, self.meta))
                elif pattern_type == "convergence":
                    checks.append(_l3.check_convergence(df, pattern, self.meta))
                elif pattern_type == "seasonal_anomaly":
                    checks.append(_l3.check_seasonal_anomaly(df, pattern, self.meta))
                elif pattern_type == "ranking_reversal":
                    checks.append(_l3.check_ranking_reversal(df, pattern, self.meta))
                else:
                    logger.debug(
                        "SchemaAwareValidator._run_l3: no check for type '%s'.",
                        pattern_type,
                    )
            except Exception as exc:
                # Pattern check raised — convert to a failed Check
                checks.append(Check(
                    name=f"pattern_{pattern_type}_{pattern.get('col', 'unknown')}",
                    passed=False,
                    detail=f"Exception during L3 check: {exc}",
                ))

        return checks
