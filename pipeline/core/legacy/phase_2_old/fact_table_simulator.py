"""
FactTableSimulator — the core SDK for AGPDS Phase 2.

LLMs write Python scripts calling this type-safe API to declare schemas,
distributions, relationships, and patterns. The deterministic `generate()`
engine converts declarations into an atomic-grain pd.DataFrame + SchemaMetadata.

Reference: phase_2.md §2.1–2.5
"""

import numpy as np
import pandas as pd
import ast
import operator
from typing import Optional, Tuple
from scipy.stats import norm

from .distributions import sample_distribution, SUPPORTED_DISTS
from .patterns import inject_pattern, PATTERN_TYPES
from .schema_metadata import SchemaMetadata


class FactTableSimulator:
    """
    Type-safe SDK for atomic-grain fact table generation.

    Usage:
        sim = FactTableSimulator(target_rows=500, seed=42)

        # Step 1: Declare columns
        sim.add_category("hospital", values=[...], weights=[...], group="entity")
        sim.add_temporal("visit_date", start="2024-01-01", end="2024-06-30", freq="daily")
        sim.add_measure("wait_minutes", dist="lognormal", params={"mu": 3.0, "sigma": 0.5})

        # Step 2: Declare relationships & patterns
        sim.add_conditional("wait_minutes", on="severity", mapping={...})
        sim.add_correlation("wait_minutes", "satisfaction", target_r=-0.55)
        sim.declare_orthogonal("entity", "patient", rationale="...")
        sim.inject_pattern("outlier_entity", target="...", col="...", params={...})

        # Generate
        df, meta = sim.generate()
    """

    def __init__(self, target_rows: int = 500, seed: int = 42):
        if target_rows < 1:
            raise ValueError(f"target_rows must be >= 1, got {target_rows}")
        self.target_rows = target_rows
        self.seed = seed

        # Step 1 storage
        self._category_specs: list[dict] = []
        self._measure_specs: list[dict] = []
        self._temporal_spec: Optional[dict] = None

        # Step 2 storage
        self._conditional_specs: list[dict] = []
        self._dependency_specs: list[dict] = []
        self._correlation_specs: list[dict] = []
        self._orthogonal_specs: list[dict] = []
        self._pattern_specs: list[dict] = []
        self._realism_spec: Optional[dict] = None

        # Dimension groups: group_name → {columns: [names], parents: {child: parent}}
        self._dimension_groups: dict[str, dict] = {}

        # Column name registry for uniqueness checks
        self._column_names: set[str] = set()

        # Ordering guard: set True after first Step 2 call
        self._frozen = False

    # ====================================================================
    # Step 1 — Column Declarations
    # ====================================================================

    def add_category(
        self,
        name: str,
        values: list,
        weights: list[float],
        group: str,
        parent: Optional[str] = None,
        conditional_weights: Optional[dict] = None,
    ) -> "FactTableSimulator":
        """
        Declare a categorical column.

        Args:
            name: Column name (must be unique).
            values: List of category values.
            weights: Probability weights (auto-normalized). Used when no
                per-parent conditional weights apply.
            group: Dimension group name.
            parent: Optional parent column within the same group (hierarchy).
            conditional_weights: Optional mapping ``{parent_value: [w, …]}``
                that overrides *weights* based on the parent column's value,
                enabling ``P(child | parent)`` sampling. Each weight list is
                auto-normalized and must have the same length as *values*.
                Requires *parent* to be set; ignored otherwise.

        Raises:
            RuntimeError: If called after a Step 2 method.
            ValueError: On invalid parameters.
        """
        self._check_not_frozen("add_category")
        self._check_unique_name(name)

        if not values:
            raise ValueError(f"add_category('{name}'): values list cannot be empty")
        if len(weights) != len(values):
            raise ValueError(
                f"add_category('{name}'): weights length ({len(weights)}) "
                f"must match values length ({len(values)})"
            )

        # Auto-normalize weights
        w = np.array(weights, dtype=float)
        if w.sum() <= 0:
            raise ValueError(f"add_category('{name}'): weights must sum to > 0")
        w = w / w.sum()

        # Validate parent
        if parent is not None:
            if group not in self._dimension_groups:
                raise ValueError(
                    f"add_category('{name}'): parent '{parent}' references "
                    f"group '{group}' which has no columns yet"
                )
            if parent not in [c["name"] for c in self._category_specs
                              if c["group"] == group]:
                raise ValueError(
                    f"add_category('{name}'): parent '{parent}' not found "
                    f"in group '{group}'"
                )

        # Validate and normalize conditional_weights
        cw_normalized: Optional[dict] = None
        if conditional_weights is not None:
            if parent is None:
                raise ValueError(
                    f"add_category('{name}'): conditional_weights requires "
                    f"a parent column to be set"
                )
            cw_normalized = {}
            for pval, pw in conditional_weights.items():
                if len(pw) != len(values):
                    raise ValueError(
                        f"add_category('{name}'): conditional_weights['{pval}'] "
                        f"has length {len(pw)}, expected {len(values)}"
                    )
                pw_arr = np.array(pw, dtype=float)
                if pw_arr.sum() <= 0:
                    raise ValueError(
                        f"add_category('{name}'): conditional_weights['{pval}'] "
                        f"must sum to > 0"
                    )
                cw_normalized[pval] = (pw_arr / pw_arr.sum()).tolist()

        # Register in dimension group
        if group not in self._dimension_groups:
            self._dimension_groups[group] = {"columns": [], "parents": {}}
        self._dimension_groups[group]["columns"].append(name)
        if parent is not None:
            self._dimension_groups[group]["parents"][name] = parent

        spec = {
            "name": name,
            "values": list(values),
            "weights": w.tolist(),
            "group": group,
            "parent": parent,
            "conditional_weights": cw_normalized,
        }
        self._category_specs.append(spec)
        self._column_names.add(name)
        return self

    def add_measure(
        self,
        name: str,
        dist: str,
        params: dict,
        scale: Optional[list[float]] = None,
    ) -> "FactTableSimulator":
        """
        Declare a numerical measure column with a named distribution.

        Args:
            name: Column name (must be unique).
            dist: Distribution name from SUPPORTED_DISTS.
            params: Distribution-specific parameters.
            scale: Optional [low, high] for bounded output rescaling.

        Raises:
            RuntimeError: If called after a Step 2 method.
            ValueError: On invalid distribution or parameters.
        """
        self._check_not_frozen("add_measure")
        self._check_unique_name(name)

        if dist not in SUPPORTED_DISTS:
            raise ValueError(
                f"add_measure('{name}'): unsupported distribution '{dist}'. "
                f"Must be one of: {', '.join(sorted(SUPPORTED_DISTS))}"
            )
        if scale is not None:
            if len(scale) != 2 or scale[0] >= scale[1]:
                raise ValueError(
                    f"add_measure('{name}'): scale must be [low, high] "
                    f"with low < high, got {scale}"
                )

        spec = {
            "name": name,
            "dist": dist,
            "params": dict(params),
            "scale": scale,
        }
        self._measure_specs.append(spec)
        self._column_names.add(name)
        return self

    def add_temporal(
        self,
        name: str,
        start: str,
        end: str,
        freq: str,
    ) -> "FactTableSimulator":
        """
        Declare a temporal dimension column.

        Args:
            name: Column name (must be unique).
            start: Start date string (e.g., "2024-01-01").
            end: End date string (e.g., "2024-06-30").
            freq: Pandas frequency string (e.g., "daily", "D", "M", "W").

        Raises:
            RuntimeError: If called after a Step 2 method.
            ValueError: On invalid dates or frequency.
        """
        self._check_not_frozen("add_temporal")
        self._check_unique_name(name)

        if self._temporal_spec is not None:
            raise ValueError(
                f"add_temporal('{name}'): only one temporal column is allowed. "
                f"Already declared: '{self._temporal_spec['name']}'"
            )

        # Normalize common frequency aliases
        freq_map = {"daily": "D", "weekly": "W", "monthly": "ME",
                     "quarterly": "QE", "yearly": "YE", "hourly": "h",
                     "h": "h", "d": "D", "w": "W", "m": "ME", "q": "QE", "y": "YE"}
        freq_norm = freq_map.get(freq.lower(), freq)
        
        # Catch upper cases like 'M', 'Q', 'Y' if LLM hallucinated
        if freq_norm == "H": freq_norm = "h"
        elif freq_norm == "M": freq_norm = "ME"
        elif freq_norm == "Q": freq_norm = "QE"
        elif freq_norm == "Y": freq_norm = "YE"

        try:
            date_range = pd.date_range(start=start, end=end, freq=freq_norm)
        except Exception as e:
            raise ValueError(
                f"add_temporal('{name}'): invalid date range — {e}"
            )

        if len(date_range) == 0:
            raise ValueError(
                f"add_temporal('{name}'): date range is empty "
                f"(start={start}, end={end}, freq={freq})"
            )

        spec = {
            "name": name,
            "start": start,
            "end": end,
            "freq": freq_norm,
            "date_range": date_range,
        }
        self._temporal_spec = spec
        self._column_names.add(name)
        return self

    # ====================================================================
    # Step 2 — Relationships & Patterns
    # ====================================================================

    def add_conditional(
        self,
        measure: str,
        on: str,
        mapping: dict,
    ) -> "FactTableSimulator":
        """
        Declare that a measure's distribution parameters vary by a category.

        Args:
            measure: Name of an already-declared measure column.
            on: Name of an already-declared categorical column.
            mapping: {category_value: {param_overrides}} for each value.

        Raises:
            ValueError: If measure or on column not found, or mapping incomplete.
        """
        self._freeze()

        measure_names = {s["name"] for s in self._measure_specs}
        if measure not in measure_names:
            raise ValueError(
                f"add_conditional: measure '{measure}' not declared. "
                f"Declared measures: {measure_names}"
            )

        cat_spec = self._find_category(on)
        if cat_spec is None:
            raise ValueError(
                f"add_conditional: categorical column '{on}' not declared"
            )

        # Check mapping covers all category values
        declared_values = set(cat_spec["values"])
        mapping_keys = set(mapping.keys())
        missing = declared_values - mapping_keys
        if missing:
            raise ValueError(
                f"add_conditional('{measure}' on '{on}'): "
                f"mapping missing values: {missing}"
            )

        measure_spec = next(s for s in self._measure_specs if s["name"] == measure)
        normalized_mapping = self._normalize_conditional_mapping(
            measure=measure,
            base_dist=measure_spec["dist"],
            mapping=mapping,
        )

        self._conditional_specs.append({
            "measure": measure,
            "on": on,
            "mapping": normalized_mapping,
        })
        return self

    def add_dependency(
        self,
        target: str,
        formula: str,
        noise_sigma: float = 0.0,
    ) -> "FactTableSimulator":
        """
        Define functional dependency: target = f(columns) + noise.

        Args:
            target: Name of an already-declared measure column.
            formula: Arithmetic expression evaluated in an isolated, restricted
                expression evaluator (basic math ops only).
            noise_sigma: Standard deviation of additive Gaussian noise.

        Raises:
            ValueError: If target not found.
        """
        self._freeze()

        measure_names = {s["name"] for s in self._measure_specs}
        if target not in measure_names:
            raise ValueError(
                f"add_dependency: target '{target}' not declared as a measure"
            )

        self._validate_dependency_correlation_conflicts(
            extra_dependency_target=target
        )

        self._dependency_specs.append({
            "target": target,
            "formula": formula,
            "noise_sigma": noise_sigma,
        })
        return self

    def add_correlation(
        self,
        col_a: str,
        col_b: str,
        target_r: float,
    ) -> "FactTableSimulator":
        """
        Inject Pearson correlation between two measures via Gaussian Copula.

        Args:
            col_a: Name of first measure column.
            col_b: Name of second measure column.
            target_r: Target Pearson correlation in [-1, 1].

        Raises:
            ValueError: If columns not found or target_r out of range.
        """
        self._freeze()

        measure_names = {s["name"] for s in self._measure_specs}
        if col_a not in measure_names:
            raise ValueError(f"add_correlation: '{col_a}' is not a declared measure")
        if col_b not in measure_names:
            raise ValueError(f"add_correlation: '{col_b}' is not a declared measure")
        if col_a == col_b:
            raise ValueError(f"add_correlation: col_a and col_b must differ")
        if abs(target_r) > 1.0:
            raise ValueError(
                f"add_correlation: target_r must be in [-1, 1], got {target_r}"
            )
        if abs(target_r) >= 1.0:
            raise ValueError(
                "add_correlation: target_r=±1 is not supported by Gaussian Copula "
                "(requires non-singular correlation matrix). Use |target_r| < 1."
            )

        spec = {
            "col_a": col_a,
            "col_b": col_b,
            "target_r": target_r,
        }
        self._validate_dependency_correlation_conflicts(
            extra_correlation=spec
        )
        self._validate_correlation_feasibility(extra_spec=spec)
        self._correlation_specs.append(spec)
        return self

    def declare_orthogonal(
        self,
        group_a: str,
        group_b: str,
        rationale: str,
    ) -> "FactTableSimulator":
        """
        Declare two dimension groups as statistically independent.

        Args:
            group_a: First dimension group name.
            group_b: Second dimension group name.
            rationale: Human-readable justification for independence.

        Raises:
            ValueError: If either group does not exist.
        """
        self._freeze()

        if group_a not in self._dimension_groups:
            raise ValueError(
                f"declare_orthogonal: group '{group_a}' not declared"
            )
        if group_b not in self._dimension_groups:
            raise ValueError(
                f"declare_orthogonal: group '{group_b}' not declared"
            )
        if group_a == group_b:
            raise ValueError(
                f"declare_orthogonal: groups must be different"
            )

        self._orthogonal_specs.append({
            "group_a": group_a,
            "group_b": group_b,
            "rationale": rationale,
        })
        return self

    def inject_pattern(
        self,
        pattern_type: str,
        target: Optional[str],
        col: Optional[str],
        params: dict,
    ) -> "FactTableSimulator":
        """
        Plant a narrative-driven statistical anomaly.

        Args:
            pattern_type: One of PATTERN_TYPES.
            target: Pandas query string to filter affected rows.
            col: Target measure column.
            params: Pattern-specific parameters.

        Raises:
            ValueError: If pattern_type is unknown.
        """
        self._freeze()

        # Handle LLM hallucination for break_point silently
        if pattern_type in ["break_point", "break-point"]:
            pattern_type = "trend_break"

        if pattern_type not in PATTERN_TYPES:
            raise ValueError(
                f"inject_pattern: unknown type '{pattern_type}'. "
                f"Must be one of: {', '.join(sorted(PATTERN_TYPES))}"
            )
        normalized_params = self._normalize_pattern_params(pattern_type, params)

        self._pattern_specs.append({
            "type": pattern_type,
            "target": target,
            "col": col,
            "params": normalized_params,
        })
        return self

    def set_realism(
        self,
        missing_rate: float = 0.0,
        dirty_rate: float = 0.0,
        censoring: Optional[dict] = None,
    ) -> "FactTableSimulator":
        """
        Simulate data imperfections.

        Args:
            missing_rate: Fraction of non-key cells to set NaN (0-0.3).
            dirty_rate: Fraction of categorical cells with typos (0-0.3).
            censoring: {"col": str, "type": "left"|"right", "threshold": float}

        Raises:
            ValueError: If rates are out of bounds.
        """
        self._freeze()

        if not 0 <= missing_rate <= 0.3:
            raise ValueError(
                f"set_realism: missing_rate must be in [0, 0.3], got {missing_rate}"
            )
        if not 0 <= dirty_rate <= 0.3:
            raise ValueError(
                f"set_realism: dirty_rate must be in [0, 0.3], got {dirty_rate}"
            )

        self._realism_spec = {
            "missing_rate": missing_rate,
            "dirty_rate": dirty_rate,
            "censoring": censoring,
        }
        return self

    # ====================================================================
    # generate() — Deterministic Engine
    # ====================================================================

    def generate(self) -> Tuple[pd.DataFrame, dict]:
        """
        Execute the 7-stage deterministic pipeline.

        Given the same seed, output is bit-for-bit reproducible.

        Returns:
            (DataFrame, SchemaMetadata dict)
        """
        rng = np.random.default_rng(self.seed)

        # β — Build Dimensional Skeleton
        df = self._build_skeleton(rng)

        # δ — Sample Marginal Distributions
        df = self._sample_measures(df, rng)

        # γ — Apply Conditional Overrides
        df = self._apply_conditionals(df, rng)

        # ψ — Inject Correlations (Gaussian Copula)
        self._validate_dependency_correlation_conflicts()
        df = self._inject_correlations(df, rng)

        # λ — Evaluate Functional Dependencies
        df = self._apply_dependencies(df, rng)

        # φ — Inject Patterns
        df = self._inject_patterns(df, rng)

        # ρ — Inject Realism
        df = self._inject_realism(df, rng)

        df = self._post_process(df)
        meta = self._build_schema_metadata(df)
        return df, meta

    # ====================================================================
    # Engine stages (private)
    # ====================================================================

    def _build_skeleton(self, rng: np.random.Generator) -> pd.DataFrame:
        """
        β — Build the dimensional skeleton.

        Spec alignment:
        - Declared orthogonal pairs are sampled independently.
        - Non-declared pairs are not forced into cross-product independence.
        """
        if not self._category_specs:
            raise ValueError("At least one categorical column is required")

        # Symmetric set: (a, b) with a < b
        orthogonal_pairs = {
            tuple(sorted((s["group_a"], s["group_b"])))
            for s in self._orthogonal_specs
        }

        # Build each dimension group to target_rows so we can control
        # pairwise independence without exploding cardinality via global cross-join.
        group_dfs: dict[str, pd.DataFrame] = {}
        for group_name, group_info in self._dimension_groups.items():
            group_df = self._build_group_samples(
                group_name, group_info, rng, n_samples=self.target_rows
            )
            group_dfs[group_name] = group_df

        # Merge groups into one row-level skeleton:
        # - If new group is orthogonal to all already merged groups, shuffle rows
        #   independently before attaching (independent sampling behavior).
        # - Otherwise keep row alignment, avoiding unconditional independence.
        combined = None
        combined_groups: list[str] = []
        for group_name, gdf in group_dfs.items():
            if combined is None:
                combined = gdf.reset_index(drop=True)
                combined_groups.append(group_name)
            else:
                is_orthogonal_to_all = all(
                    tuple(sorted((group_name, prev_group))) in orthogonal_pairs
                    for prev_group in combined_groups
                )
                attach_df = gdf.reset_index(drop=True)
                if is_orthogonal_to_all:
                    perm = rng.permutation(len(attach_df))
                    attach_df = attach_df.iloc[perm].reset_index(drop=True)

                combined = pd.concat(
                    [combined.reset_index(drop=True), attach_df], axis=1
                )
                combined_groups.append(group_name)

        if combined is None or len(combined) == 0:
            raise ValueError("Failed to build dimensional skeleton")

        df = combined.iloc[: self.target_rows].reset_index(drop=True)

        # Add temporal column by sampling from date_range
        if self._temporal_spec is not None:
            date_range = self._temporal_spec["date_range"]
            temporal_values = rng.choice(date_range, size=len(df))
            df[self._temporal_spec["name"]] = temporal_values

        return df

    def _build_group_samples(
        self,
        group_name: str,
        group_info: dict,
        rng: np.random.Generator,
        n_samples: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Build samples for one dimension group, respecting parent-child hierarchy.

        Returns a DataFrame with one column per category in the group,
        with enough rows for a reasonable cross-join base.
        """
        columns = group_info["columns"]
        parents = group_info["parents"]

        # Find root columns (no parent)
        roots = [c for c in columns if c not in parents]

        # Number of rows to sample for this group.
        if n_samples is None:
            n_samples = self.target_rows

        result = pd.DataFrame()

        # Sample root columns
        for root in roots:
            spec = self._find_category(root)
            values = rng.choice(
                spec["values"],
                size=n_samples,
                p=spec["weights"],
            )
            result[root] = values

        # Sample child columns conditioned on parent
        # Process in topological order
        processed = set(roots)
        remaining = [c for c in columns if c not in processed]
        max_iters = len(remaining) + 1
        while remaining and max_iters > 0:
            max_iters -= 1
            for child in list(remaining):
                parent_col = parents.get(child)
                if parent_col in processed:
                    spec = self._find_category(child)
                    cw = spec.get("conditional_weights")
                    if cw and parent_col is not None and parent_col in result.columns:
                        # Per-parent-value conditional sampling: P(child | parent)
                        parent_vals = result[parent_col].values
                        child_values = np.empty(n_samples, dtype=object)
                        for pval in np.unique(parent_vals):
                            mask = parent_vals == pval
                            pw = cw.get(str(pval)) or cw.get(pval)
                            if pw is None:
                                # Fall back to global weights for unseen parent values
                                pw = spec["weights"]
                            child_values[mask] = rng.choice(
                                spec["values"],
                                size=int(mask.sum()),
                                p=pw,
                            )
                    else:
                        # No conditional weights declared — sample independently
                        child_values = rng.choice(
                            spec["values"],
                            size=n_samples,
                            p=spec["weights"],
                        )
                    result[child] = child_values
                    processed.add(child)
                    remaining.remove(child)

        return result

    def _sample_measures(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """δ — Sample marginal distributions for each measure."""
        n = len(df)
        for spec in self._measure_specs:
            df[spec["name"]] = sample_distribution(
                spec["dist"], spec["params"], n, rng, scale=spec.get("scale")
            )
        return df

    def _apply_conditionals(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """γ — Override measure values per-category using conditional mappings."""
        for cond in self._conditional_specs:
            measure = cond["measure"]
            on_col = cond["on"]
            mapping = cond["mapping"]

            # Find the measure's base distribution
            measure_spec = next(
                s for s in self._measure_specs if s["name"] == measure
            )
            base_dist = measure_spec["dist"]

            for cat_value, param_overrides in mapping.items():
                mask = df[on_col] == cat_value
                count = mask.sum()
                if count == 0:
                    continue

                # Merge base params with overrides
                merged_params = {**measure_spec["params"], **param_overrides}
                new_values = sample_distribution(
                    base_dist, merged_params, count, rng,
                    scale=measure_spec.get("scale"),
                )
                df.loc[mask, measure] = new_values

        return df

    def _apply_dependencies(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """λ — Evaluate add_dependency() formulas."""
        for dep in self._dependency_specs:
            target = dep["target"]
            formula = dep["formula"]
            noise_sigma = dep["noise_sigma"]

            # Build evaluation context with categorical lookups
            # e.g., "severity_base" → numeric map from conditional
            eval_context = self._build_eval_context(df)

            local_vars = {col: df[col] for col in df.columns}
            local_vars.update(eval_context)
            try:
                predicted = _safe_eval_formula(formula, local_vars)
            except Exception as e2:
                raise ValueError(
                    f"Dependency formula '{formula}' for '{target}' failed: {e2}"
                ) from e2

            if noise_sigma > 0:
                noise = rng.normal(0, noise_sigma, len(df))
                predicted = predicted + noise

            df[target] = predicted

        return df

    def _build_eval_context(self, df: pd.DataFrame) -> dict:
        """
        Build a context dict for formula evaluation.

        For each conditional mapping, create a "{on}_{measure}" column
        mapping categorical values to their mean parameter value,
        enabling formulas like "wait_minutes * 12 + severity_base".
        """
        context = {}
        for cond in self._conditional_specs:
            on_col = cond["on"]
            measure = cond["measure"]
            mapping = cond["mapping"]

            # Create a numeric lookup: category → first numeric param value
            numeric_map = {}
            for cat_val, params in mapping.items():
                # Use 'mu' if available, else first numeric value
                if "mu" in params:
                    numeric_map[cat_val] = params["mu"]
                elif "mean" in params:
                    numeric_map[cat_val] = params["mean"]
                else:
                    # Use first numeric value in params
                    for v in params.values():
                        if isinstance(v, (int, float)):
                            numeric_map[cat_val] = v
                            break

            if numeric_map:
                var_name = f"{on_col}_base"
                context[var_name] = df[on_col].map(numeric_map).fillna(0)

        return context

    def _inject_correlations(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """
        ψ — Inject Pearson correlations via Gaussian Copula.

        Algorithm:
        1. Rank each measure column → uniform margins
        2. Transform to normal margins via inverse CDF
        3. Apply Cholesky decomposition with target correlation matrix
        4. Transform back to uniform → back to original marginal
        """
        if not self._correlation_specs:
            return df

        self._validate_correlation_feasibility()
        n = len(df)
        if n < 3:
            return df

        components = self._get_correlation_components()
        for cols in components:
            if len(cols) < 2:
                continue

            corr_matrix = np.eye(len(cols), dtype=float)
            idx = {c: i for i, c in enumerate(cols)}
            for spec in self._correlation_specs:
                a, b = spec["col_a"], spec["col_b"]
                if a in idx and b in idx:
                    i, j = idx[a], idx[b]
                    corr_matrix[i, j] = spec["target_r"]
                    corr_matrix[j, i] = spec["target_r"]

            eigvals = np.linalg.eigvalsh(corr_matrix)
            if np.any(eigvals <= 1e-10):
                raise ValueError(
                    f"Cannot inject correlations for columns {cols}: "
                    "target matrix is not positive-definite."
                )

            L = np.linalg.cholesky(corr_matrix)
            z_uncorr = rng.standard_normal((n, len(cols)))
            z_corr = z_uncorr @ L.T
            u_corr = norm.cdf(z_corr)

            for j, col in enumerate(cols):
                orig_sorted = np.sort(df[col].values.astype(float))
                rank_idx = np.argsort(np.argsort(u_corr[:, j]))
                df[col] = orig_sorted[rank_idx]

        return df

    def _validate_correlation_feasibility(
        self, extra_spec: Optional[dict] = None
    ) -> None:
        """Validate that each connected correlation block is positive-definite."""
        specs = list(self._correlation_specs)
        if extra_spec is not None:
            specs.append(extra_spec)
        if not specs:
            return

        # Build adjacency for connected components.
        graph: dict[str, set[str]] = {}
        for s in specs:
            a, b = s["col_a"], s["col_b"]
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)

        visited = set()
        for start in graph:
            if start in visited:
                continue
            stack = [start]
            comp = []
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                comp.append(node)
                stack.extend(graph[node] - visited)
            if len(comp) < 2:
                continue

            idx = {c: i for i, c in enumerate(comp)}
            corr_matrix = np.eye(len(comp), dtype=float)
            for s in specs:
                a, b = s["col_a"], s["col_b"]
                if a in idx and b in idx:
                    i, j = idx[a], idx[b]
                    corr_matrix[i, j] = s["target_r"]
                    corr_matrix[j, i] = s["target_r"]

            eigvals = np.linalg.eigvalsh(corr_matrix)
            if np.any(eigvals <= 1e-10):
                raise ValueError(
                    "add_correlation: target correlations are infeasible as a joint "
                    f"matrix for block {comp}. Consider relaxing target_r values."
                )

    def _get_correlation_components(self) -> list[list[str]]:
        """Return connected components from declared correlation pairs."""
        if not self._correlation_specs:
            return []
        graph: dict[str, set[str]] = {}
        for s in self._correlation_specs:
            a, b = s["col_a"], s["col_b"]
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)

        comps: list[list[str]] = []
        seen = set()
        for root in graph:
            if root in seen:
                continue
            stack = [root]
            comp = []
            while stack:
                node = stack.pop()
                if node in seen:
                    continue
                seen.add(node)
                comp.append(node)
                stack.extend(graph[node] - seen)
            comps.append(sorted(comp))
        return comps

    def _inject_patterns(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """φ — Inject each declared pattern."""
        # Identify temporal and root entity columns for pattern handlers
        temporal_col = self._temporal_spec["name"] if self._temporal_spec else None
        root_entity_col = self._get_root_entity_col()

        for spec in self._pattern_specs:
            df = inject_pattern(
                df,
                pattern_type=spec["type"],
                target=spec["target"],
                col=spec["col"],
                params=spec["params"],
                temporal_col=temporal_col,
                root_entity_col=root_entity_col,
                rng=rng,
            )
        return df

    def _inject_realism(
        self, df: pd.DataFrame, rng: np.random.Generator
    ) -> pd.DataFrame:
        """ρ — Inject missing data, dirty values, and censoring."""
        if self._realism_spec is None:
            return df

        spec = self._realism_spec
        n_rows, n_cols = df.shape

        # Primary keys = all categorical columns (never inject missing into these)
        pk_cols = {s["name"] for s in self._category_specs}
        if self._temporal_spec:
            pk_cols.add(self._temporal_spec["name"])

        # Missing data
        missing_rate = spec["missing_rate"]
        if missing_rate > 0:
            for col in df.columns:
                if col in pk_cols:
                    continue
                mask = rng.random(n_rows) < missing_rate
                df.loc[mask, col] = np.nan

        # Dirty values (swap to wrong category, preserving cardinality)
        dirty_rate = spec["dirty_rate"]
        if dirty_rate > 0:
            for cat_spec in self._category_specs:
                col = cat_spec["name"]
                valid_values = cat_spec["values"]
                if len(valid_values) < 2:
                    continue  # Can't swap with only one value
                mask = rng.random(n_rows) < dirty_rate
                n_dirty = mask.sum()
                if n_dirty > 0:
                    # Replace with a different valid value (simulates
                    # data entry errors while preserving cardinality)
                    current = df.loc[mask, col].values
                    swapped = np.array([
                        rng.choice([v for v in valid_values if v != c])
                        for c in current
                    ])
                    df.loc[mask, col] = swapped

        # Censoring
        censoring = spec.get("censoring")
        if censoring is not None:
            cens_col = censoring["col"]
            cens_type = censoring.get("type", "right")
            threshold = censoring["threshold"]
            if cens_type == "right":
                df.loc[df[cens_col] > threshold, cens_col] = threshold
            elif cens_type == "left":
                df.loc[df[cens_col] < threshold, cens_col] = threshold

        return df

    def _post_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final cleanup: sort by temporal column if present, reset index."""
        if self._temporal_spec is not None:
            df = df.sort_values(self._temporal_spec["name"]).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)
        return df

    def _build_schema_metadata(self, df: "pd.DataFrame") -> dict:
        """Build the SchemaMetadata dict from internal declarations and the generated DataFrame."""
        # Dimension groups
        dim_groups = {}
        for group_name, info in self._dimension_groups.items():
            columns = info["columns"]
            parents = info["parents"]
            # Build hierarchy: root → children in order
            roots = [c for c in columns if c not in parents]
            hierarchy = list(roots)
            # Add children in topological order
            remaining = [c for c in columns if c in parents]
            while remaining:
                for child in list(remaining):
                    parent = parents[child]
                    if parent in hierarchy:
                        hierarchy.append(child)
                        remaining.remove(child)

            dim_groups[group_name] = {
                "columns": columns,
                "hierarchy": hierarchy,
            }

        # Build set of groups that participate in orthogonal declarations
        orthogonal_groups = set()
        for o in self._orthogonal_specs:
            orthogonal_groups.add(o["group_a"])
            orthogonal_groups.add(o["group_b"])

        # Columns metadata
        columns_meta = []
        for spec in self._category_specs:
            role = "secondary" if spec["parent"] is not None else "primary"
            entry = {
                "name": spec["name"],
                "type": "categorical",
                "role": role,
                "group": spec["group"],
                "parent": spec["parent"],
                "cardinality": len(spec["values"]),
            }
            if spec["group"] in orthogonal_groups:
                entry["orthogonal"] = True
            columns_meta.append(entry)
        if self._temporal_spec:
            columns_meta.append({
                "name": self._temporal_spec["name"],
                "type": "temporal",
                "role": "temporal",
            })
        for spec in self._measure_specs:
            columns_meta.append({
                "name": spec["name"],
                "type": "measure",
                "role": "measure",
                "declared_dist": spec["dist"],
                "declared_params": spec["params"],
                "scale": spec.get("scale"),
            })

        # Conditionals
        conditionals = [
            {"measure": c["measure"], "on": c["on"], "mapping": c["mapping"]}
            for c in self._conditional_specs
        ]

        # Correlations
        correlations = [
            {"col_a": c["col_a"], "col_b": c["col_b"], "target_r": c["target_r"]}
            for c in self._correlation_specs
        ]

        # Dependencies
        dependencies = [
            {"target": d["target"], "formula": d["formula"]}
            for d in self._dependency_specs
        ]

        # Patterns — store all fields flat at top level (spec §2.3)
        patterns = []
        for p in self._pattern_specs:
            pat_entry: dict = {"type": p["type"]}
            if p["target"] is not None:
                pat_entry["target"] = p["target"]
            if p["col"] is not None:
                pat_entry["col"] = p["col"]
            # Expand params dict keys directly into the pattern entry
            # so Phase 3 can read p["break_point"], p["metrics"], etc. without
            # needing to know about the nested "params" layer.
            for k, v in p["params"].items():
                pat_entry[k] = v
            patterns.append(pat_entry)

        return {
            "dimension_groups": dim_groups,
            "orthogonal_groups": [
                {"group_a": o["group_a"], "group_b": o["group_b"],
                 "rationale": o["rationale"]}
                for o in self._orthogonal_specs
            ],
            "columns": columns_meta,
            "conditionals": conditionals,
            "correlations": correlations,
            "dependencies": dependencies,
            "patterns": patterns,
            "realism": self._realism_spec if self._realism_spec else {},
            "total_rows": self.target_rows,
            "actual_rows": len(df),
        }

    # ====================================================================
    # Helpers
    # ====================================================================

    def _check_not_frozen(self, method_name: str) -> None:
        """Raise if Step 2 methods have already been called."""
        if self._frozen:
            raise RuntimeError(
                f"Cannot call {method_name}() after relationship/pattern "
                f"declarations. All column declarations (add_category, "
                f"add_measure, add_temporal) must precede relationship "
                f"declarations (add_conditional, add_dependency, etc.)."
            )

    def _freeze(self) -> None:
        """Mark Step 1 as complete."""
        self._frozen = True

    def _check_unique_name(self, name: str) -> None:
        """Ensure column name hasn't been used."""
        if name in self._column_names:
            raise ValueError(f"Column name '{name}' is already declared")

    def _find_category(self, name: str) -> Optional[dict]:
        """Find a category spec by name."""
        for spec in self._category_specs:
            if spec["name"] == name:
                return spec
        return None

    def _normalize_conditional_mapping(
        self,
        measure: str,
        base_dist: str,
        mapping: dict,
    ) -> dict:
        """
        Normalize conditional mapping into flat parameter overrides.

        Accepts either:
        - flat format: {"mu": 4.5, "sigma": 0.4}
        - nested format: {"dist": "...", "params": {...}}
        """
        normalized = {}
        for cat_value, overrides in mapping.items():
            if not isinstance(overrides, dict):
                raise ValueError(
                    f"add_conditional('{measure}'): mapping['{cat_value}'] "
                    "must be a dict of parameter overrides"
                )

            flat_overrides = dict(overrides)
            if "params" in flat_overrides and isinstance(flat_overrides["params"], dict):
                nested_dist = flat_overrides.get("dist")
                if nested_dist is not None and nested_dist != base_dist:
                    raise ValueError(
                        f"add_conditional('{measure}'): mapping['{cat_value}'] "
                        f"declares dist='{nested_dist}', but measure uses "
                        f"dist='{base_dist}'"
                    )
                flat_overrides = dict(flat_overrides["params"])

            normalized[cat_value] = flat_overrides

        return normalized

    def _normalize_pattern_params(self, pattern_type: str, params: dict) -> dict:
        """Normalize legacy/alias pattern parameter names to canonical keys."""
        normalized = dict(params)
        if pattern_type == "outlier_entity":
            if "z_score" not in normalized and "multiplier" in normalized:
                normalized["z_score"] = normalized.pop("multiplier")
            else:
                normalized.pop("multiplier", None)
        elif pattern_type == "trend_break":
            if "magnitude" not in normalized and "factor" in normalized:
                normalized["magnitude"] = normalized.pop("factor")
            else:
                normalized.pop("factor", None)
        return normalized

    def _validate_dependency_correlation_conflicts(
        self,
        extra_dependency_target: Optional[str] = None,
        extra_correlation: Optional[dict] = None,
    ) -> None:
        """
        Reject declaring correlations over dependency target columns.

        Dependency targets are formula-derived outputs whose relationships are
        determined by the formula itself.
        """
        dependency_targets = {d["target"] for d in self._dependency_specs}
        if extra_dependency_target is not None:
            dependency_targets.add(extra_dependency_target)

        correlation_specs = list(self._correlation_specs)
        if extra_correlation is not None:
            correlation_specs.append(extra_correlation)

        for spec in correlation_specs:
            col_a = spec["col_a"]
            col_b = spec["col_b"]
            if col_a in dependency_targets or col_b in dependency_targets:
                raise ValueError(
                    "add_correlation: dependency target columns cannot be used in "
                    "correlation declarations because dependency formulas determine "
                    "their final values."
                )

    def _get_root_entity_col(self) -> Optional[str]:
        """Get the root column of the first dimension group."""
        if not self._dimension_groups:
            return None
        first_group = next(iter(self._dimension_groups.values()))
        roots = [c for c in first_group["columns"]
                 if c not in first_group["parents"]]
        return roots[0] if roots else None


def _rank_to_uniform(x: np.ndarray) -> np.ndarray:
    """Convert values to uniform(0, 1) via rank transformation."""
    n = len(x)
    ranks = np.empty_like(x)
    order = np.argsort(x)
    ranks[order] = np.arange(1, n + 1)
    return ranks / (n + 1)


_ALLOWED_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval_formula(formula: str, local_vars: dict):
    """Evaluate arithmetic expressions in an isolated, restricted AST evaluator."""
    expr = ast.parse(formula, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are allowed in dependency formulas")
        if isinstance(node, ast.Name):
            if node.id not in local_vars:
                raise ValueError(
                    f"Unknown variable '{node.id}' in dependency formula"
                )
            return local_vars[node.id]
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_BINARY_OPS:
                raise ValueError(
                    f"Unsupported operator '{op_type.__name__}' in dependency formula"
                )
            return _ALLOWED_BINARY_OPS[op_type](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_UNARY_OPS:
                raise ValueError(
                    f"Unsupported unary operator '{op_type.__name__}' in dependency formula"
                )
            return _ALLOWED_UNARY_OPS[op_type](_eval(node.operand))
        raise ValueError(
            f"Unsupported expression node '{type(node).__name__}' in dependency formula"
        )

    return _eval(expr)
