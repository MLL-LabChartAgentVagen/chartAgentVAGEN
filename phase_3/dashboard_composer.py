import pandas as pd
from typing import List, Optional

from view_spec import ViewSpec
from dashboard import Dashboard


class DashboardComposer:
    """Compose multi-chart dashboards from enumerated single views."""

    COMPOSITION_PATTERNS = {
        "same_type_compare":     {"k": 2, "rel": "comparative"},
        "overview_detail":       {"k": 2, "rel": "drill_down"},
        "orthogonal_contrast":   {"k": 2, "rel": "orthogonal_slice"},
        "dual_metric":           {"k": 2, "rel": "dual_metric"},
        "distribution_cause":    {"k": 2, "rel": "associative"},
        "cause_mediator_effect": {"k": 3, "rel": "causal_chain"},
        "summary_dual_detail":   {"k": 3, "rel": "drill_down+dual_metric"},
        "full_dashboard":        {"k": 4, "rel": "mixed"},
    }

    def compose(self, feasible_views: List[ViewSpec],
                schema_metadata: dict,
                target_k: int) -> List[Dashboard]:
        """Generate dashboard candidates for a given plot count."""
        dashboards = []
        for pattern_name, spec in self.COMPOSITION_PATTERNS.items():
            if spec["k"] != target_k:
                continue
            candidates = self._match_pattern(
                pattern_name, feasible_views, schema_metadata)
            dashboards.extend(candidates)
        return dashboards

    def _match_pattern(self, pattern: str, views: List[ViewSpec],
                       schema: dict) -> List[Dashboard]:
        """Match feasible views to a composition pattern."""
        results = []

        if pattern == "same_type_compare":
            # Find views with temporal dimension; split by time midpoint
            for v in views:
                if self._has_temporal(v) and v.extracted_view is not None:
                    midpoint = self._compute_temporal_midpoint(v)
                    if midpoint is None:
                        continue
                    v1 = v.with_filter(f"{v.binding['time']} < '{midpoint}'")
                    v2 = v.with_filter(f"{v.binding['time']} >= '{midpoint}'")
                    results.append(Dashboard(
                        views=[v1, v2], relationship="comparative",
                        pattern=pattern))

        elif pattern == "overview_detail":
            # Pair: aggregated overview (pie/bar) + detail (grouped_bar/stacked_bar)
            overviews = [v for v in views
                         if v.chart_type in ("pie_chart", "bar_chart")
                         and v.uses_role("primary")
                         and not v.uses_role("secondary")]
            details = [v for v in views
                       if v.chart_type in ("grouped_bar_chart", "stacked_bar_chart")
                       and v.uses_role("primary") and v.uses_role("secondary")]
            for ov in overviews:
                for det in details:
                    if ov.measure == det.measure:
                        results.append(Dashboard(
                            views=[ov, det], relationship="drill_down",
                            pattern=pattern))

        elif pattern == "orthogonal_contrast":
            # Pair: same metric, grouped by primary vs. grouped by orthogonal
            # ONLY use declared orthogonal pairs from schema_metadata
            ortho_pairs = schema.get("orthogonal_pairs", [])
            primary_views = [v for v in views
                             if v.uses_role("primary")
                             and not v.uses_role("orthogonal")]
            ortho_views = [v for v in views
                           if v.uses_role("orthogonal")
                           and not v.uses_role("primary")]
            for pv in primary_views:
                for ov in ortho_views:
                    if pv.measure != ov.measure:
                        continue
                    # Verify this is a declared orthogonal pair
                    pv_cat = pv.binding.get("cat") or pv.binding.get("cat1")
                    ov_cat = ov.binding.get("cat") or ov.binding.get("cat1")
                    if self._is_declared_orthogonal(pv_cat, ov_cat, ortho_pairs):
                        results.append(Dashboard(
                            views=[pv, ov], relationship="orthogonal_slice",
                            pattern=pattern))

        elif pattern == "dual_metric":
            # Pair: same GROUP BY key, different measures
            for i, v1 in enumerate(views):
                for v2 in views[i+1:]:
                    if (v1.chart_type == v2.chart_type
                            and v1.group_key == v2.group_key
                            and v1.measure != v2.measure):
                        results.append(Dashboard(
                            views=[v1, v2], relationship="dual_metric",
                            pattern=pattern))

        elif pattern == "distribution_cause":
            # Pair: distribution chart + relationship chart sharing a measure
            dist_views = [v for v in views
                          if v.chart_type in ("histogram", "box_plot", "violin_plot")]
            rel_views = [v for v in views
                         if v.chart_type in ("scatter_plot", "bubble_chart")]
            for dv in dist_views:
                for rv in rel_views:
                    if dv.measure in (rv.binding.get("m1"), rv.binding.get("m2")):
                        results.append(Dashboard(
                            views=[dv, rv], relationship="associative",
                            pattern=pattern))

        elif pattern == "cause_mediator_effect":
            # Triple: requires dependency chain from schema metadata
            deps = schema.get("dependencies", [])
            corrs = schema.get("correlations", [])
            if deps and corrs:
                chain = self._build_causal_chain(deps, corrs, views)
                if chain:
                    results.append(Dashboard(
                        views=chain, relationship="causal_chain",
                        pattern=pattern))

        elif pattern == "full_dashboard":
            # Select 4 views maximizing chart_type family diversity
            if len(views) >= 4:
                selected = self._maximize_type_diversity(views, k=4)
                results.append(Dashboard(
                    views=selected, relationship="mixed",
                    pattern=pattern))

        return results

    def _is_declared_orthogonal(self, col_a: str, col_b: str,
                                 ortho_pairs: list) -> bool:
        """Check if (col_a, col_b) is a declared orthogonal pair."""
        for pair in ortho_pairs:
            if set([pair["col_a"], pair["col_b"]]) == set([col_a, col_b]):
                return True
        return False

    def _build_causal_chain(self, deps, corrs, views) -> Optional[List[ViewSpec]]:
        """Find 3 views covering a cause → mediator → effect chain."""
        # Identify cause and effect from dependencies
        for dep in deps:
            target_col = dep["target"]
            # Find source columns mentioned in formula
            source_cols = self._extract_formula_columns(dep["formula"])
            # Find correlations involving source columns
            for corr in corrs:
                mediator_candidates = set([corr["col_a"], corr["col_b"]]) - source_cols
                if mediator_candidates:
                    mediator = mediator_candidates.pop()
                    cause = (source_cols & set([corr["col_a"], corr["col_b"]])).pop()
                    # Find views covering cause, mediator, and target
                    cause_view = self._find_view_for_measure(views, cause)
                    med_view = self._find_view_for_measure(views, mediator)
                    effect_view = self._find_view_for_measure(views, target_col)
                    if cause_view and med_view and effect_view:
                        return [cause_view, med_view, effect_view]
        return None

    def _maximize_type_diversity(self, views: List[ViewSpec],
                                  k: int) -> List[ViewSpec]:
        """Greedily select k views maximizing distinct chart families."""
        selected, used_families = [], set()
        selected_ids: set = set()
        # Priority: one view per family
        for v in views:
            if v.family not in used_families and len(selected) < k:
                selected.append(v)
                selected_ids.add(id(v))
                used_families.add(v.family)
        # Fill remaining slots — use id() to avoid ambiguous DataFrame truth-value
        for v in views:
            if id(v) not in selected_ids and len(selected) < k:
                selected.append(v)
                selected_ids.add(id(v))
        return selected[:k]

    # ── Missing helpers ──────────────────────────────────────────────────────

    def _has_temporal(self, view: ViewSpec) -> bool:
        """Return True if the view binding contains a 'time' slot."""
        return bool(view.binding.get("time"))

    def _compute_temporal_midpoint(self, view: ViewSpec) -> Optional[str]:
        """Return the median time value from the view's extracted_view as a string.

        Returns None if extracted_view is not yet populated.
        """
        if view.extracted_view is None:
            return None
        time_col = view.binding["time"]
        if time_col not in view.extracted_view.columns:
            return None
        times = pd.to_datetime(view.extracted_view[time_col])
        midpoint = times.sort_values().iloc[len(times) // 2]
        return str(midpoint.date())

    def _find_view_for_measure(self, views: List[ViewSpec],
                                measure: str) -> Optional[ViewSpec]:
        """Return the first view whose primary measure matches the target column."""
        for v in views:
            if v.measure == measure:
                return v
        return None