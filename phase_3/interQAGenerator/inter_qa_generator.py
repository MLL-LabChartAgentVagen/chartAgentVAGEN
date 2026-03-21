import random
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dashboard import Dashboard
from .inter_view_templates import INTER_VIEW_TEMPLATES


class InterQAGenerator:
    def __init__(self, templates: Dict[str, Dict[str, Any]] = None):
        if templates is None:
            self.templates = INTER_VIEW_TEMPLATES
        else:
            self.templates = templates

    def generate_qa(self, dashboard: Dashboard) -> Tuple[str, str]:
        """
        Generates a random cross-view question and answer for the given Dashboard.
        """
        if not self._views_have_data(dashboard):
            return "No data available across views", "N/A"

        applicable_templates = self._filter_templates(dashboard.relationship)
        if not applicable_templates:
            return f"No templates available for relationship '{dashboard.relationship}'", "N/A"

        template_name = random.choice(list(applicable_templates.keys()))
        t_data = applicable_templates[template_name]

        try:
            return self._apply_template(template_name, t_data, dashboard)
        except Exception as e:
            return f"Error generating QA for {template_name}: {e}", "N/A"

    def generate_all_qa(self, dashboard: Dashboard) -> List[dict]:
        """
        Generates one QA pair for each applicable template for the given Dashboard.
        """
        if not self._views_have_data(dashboard):
            return []

        applicable_templates = self._filter_templates(dashboard.relationship)

        qa_pairs = []
        for template_name, t_data in applicable_templates.items():
            try:
                q, a = self._apply_template(template_name, t_data, dashboard)
                qa_pairs.append({
                    "template": template_name,
                    "question": q,
                    "answer": a,
                    "difficulty": t_data.get("difficulty", "unknown")
                })
            except Exception:
                pass

        return qa_pairs

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _views_have_data(self, dashboard: Dashboard) -> bool:
        """Return True only if every view in the dashboard has a non-empty extracted_view."""
        return all(
            v.extracted_view is not None and not v.extracted_view.empty
            for v in dashboard.views
        )

    def _filter_templates(self, relationship: str) -> Dict[str, Dict[str, Any]]:
        """Return templates whose required_rel matches the dashboard relationship."""
        result = {}
        for name, t_data in self.templates.items():
            req = t_data.get("required_rel", [])
            if "any" in req or relationship in req:
                result[name] = t_data
        return result

    def _shared_cat(self, dashboard: Dashboard) -> Optional[str]:
        """Find a category column shared across all views; fall back to first view's first group_by."""
        if not dashboard.views:
            return None
        group_sets = [set(v.group_by) for v in dashboard.views if v.group_by]
        if not group_sets:
            return dashboard.views[0].binding.get("cat") or dashboard.views[0].binding.get("cat1")
        shared = group_sets[0].intersection(*group_sets[1:])
        if shared:
            # Preserve insertion order from first view
            for col in dashboard.views[0].group_by:
                if col in shared:
                    return col
        # No shared column — fall back to first view's first group_by
        return dashboard.views[0].group_by[0] if dashboard.views[0].group_by else None

    # ── Template dispatch ─────────────────────────────────────────────────────

    def _apply_template(
        self, template_name: str, t_data: dict, dashboard: Dashboard
    ) -> Tuple[str, str]:
        q_template = t_data["template"]
        views = dashboard.views

        if template_name == "ranking_consistency":
            return self._apply_ranking_consistency(q_template, views)

        elif template_name == "conditional_lookup":
            return self._apply_conditional_lookup(q_template, views)

        elif template_name == "trend_divergence":
            return self._apply_trend_divergence(q_template, views)

        elif template_name == "drilldown_verification":
            return self._apply_drilldown_verification(q_template, views)

        elif template_name == "orthogonal_reasoning":
            return self._apply_orthogonal_reasoning(q_template, views)

        elif template_name == "causal_inference":
            return self._apply_causal_inference(q_template, views)

        elif template_name == "holistic_synthesis":
            return self._apply_holistic_synthesis(q_template, views)

        return f"Unhandled template: {template_name}", "N/A"

    # ── Per-template apply methods ────────────────────────────────────────────

    def _apply_ranking_consistency(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Find the entity with the highest m1 in Chart A,
        then return its rank for m2 in Chart B.
        """
        v_a, v_b = views[0], views[1]
        df_a, df_b = v_a.extracted_view, v_b.extracted_view
        m1 = v_a.measure
        m2 = v_b.measure
        cat = self._resolve_shared_cat([v_a, v_b])

        if not cat or not m1 or not m2:
            return "Insufficient bindings for ranking_consistency", "N/A"
        if cat not in df_a.columns or m1 not in df_a.columns:
            return "Required columns missing in Chart A", "N/A"
        if cat not in df_b.columns or m2 not in df_b.columns:
            return "Required columns missing in Chart B", "N/A"

        q = q_template.format(cat=cat, m1=m1, m2=m2)
        ans = self._cross_rank_lookup(df_a, df_b, cat, m1, m2)
        return q, str(ans)

    def _apply_conditional_lookup(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Pick a random entity from Chart A, note its measure value,
        then look up that entity's other_measure in Chart B.
        """
        v_a, v_b = views[0], views[1]
        df_a, df_b = v_a.extracted_view, v_b.extracted_view
        measure = v_a.measure
        other_measure = v_b.measure
        cat = self._resolve_shared_cat([v_a, v_b])

        if not cat or not measure or not other_measure:
            return "Insufficient bindings for conditional_lookup", "N/A"
        if cat not in df_a.columns or measure not in df_a.columns:
            return "Required columns missing in Chart A", "N/A"

        entity = random.choice(df_a[cat].unique().tolist())
        value_series = df_a.loc[df_a[cat] == entity, measure]
        if value_series.empty:
            return "Entity not found in Chart A", "N/A"
        value = round(float(value_series.values[0]), 2)

        q = q_template.format(
            cat=cat, measure=measure, value=value, other_measure=other_measure
        )
        ans = self._conditional_value_transfer(df_b, entity, cat, other_measure)
        return q, str(ans)

    def _apply_trend_divergence(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Pick two entities. Check if they show the same trend direction
        for the shared measure across both views.
        """
        v_a, v_b = views[0], views[1]
        df_a, df_b = v_a.extracted_view, v_b.extracted_view
        measure = v_a.measure or v_b.measure
        cat = self._resolve_shared_cat([v_a, v_b])

        if not cat or not measure:
            return "Insufficient bindings for trend_divergence", "N/A"
        if cat not in df_a.columns or measure not in df_a.columns:
            return "Required columns missing in Chart A", "N/A"

        entities = df_a[cat].unique().tolist()
        if len(entities) < 2:
            return "Not enough entities for trend comparison", "N/A"

        entity_a, entity_b = random.sample(entities, 2)
        q = q_template.format(entity_a=entity_a, entity_b=entity_b, measure=measure)
        ans = self._compare_trend_directions(df_a, df_b, entity_a, entity_b, cat, measure)
        return q, str(ans)

    def _apply_drilldown_verification(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Identify the dominant category in Chart A (overview),
        then find which sub-category drives it in Chart B (detail).
        """
        v_a, v_b = views[0], views[1]
        df_a, df_b = v_a.extracted_view, v_b.extracted_view
        measure = v_a.measure
        cat_a = self._resolve_shared_cat([v_a, v_b])

        if not cat_a or not measure:
            return "Insufficient bindings for drilldown_verification", "N/A"
        if cat_a not in df_a.columns or measure not in df_a.columns:
            return "Required columns missing in Chart A", "N/A"

        dominant = df_a.loc[df_a[measure].idxmax(), cat_a]
        q = q_template.format(cat_a=dominant)
        ans = self._identify_dominant_subcategory(df_b, dominant, cat_a, measure)
        return q, str(ans)

    def _apply_orthogonal_reasoning(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Chart A groups by primary_cat; Chart B groups by ortho_cat.
        Check if the top entity in Chart A also dominates within each ortho group.
        """
        v_a, v_b = views[0], views[1]
        df_a, df_b = v_a.extracted_view, v_b.extracted_view
        measure = v_a.measure or v_b.measure
        primary_cat = v_a.binding.get("cat") or v_a.binding.get("cat1")
        ortho_cat = v_b.binding.get("cat") or v_b.binding.get("cat1")

        if not primary_cat or not ortho_cat or not measure:
            return "Insufficient bindings for orthogonal_reasoning", "N/A"
        if primary_cat not in df_a.columns or measure not in df_a.columns:
            return "Required columns missing in Chart A", "N/A"

        q = q_template.format(
            measure=measure, primary_cat=primary_cat, ortho_cat=ortho_cat
        )
        ans = self._verify_orthogonal_dominance(df_a, df_b, primary_cat, ortho_cat, measure)
        return q, str(ans)

    def _apply_causal_inference(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Requires 3 views. Interprets them as cause → mediator → effect.
        Detects direction of change in each and explains the pattern.
        """
        if len(views) < 3:
            return "causal_inference requires 3 views", "N/A"

        cause = views[0].measure
        mediator = views[1].measure
        effect = views[2].measure

        if not cause or not mediator or not effect:
            return "Insufficient measure bindings for causal_inference", "N/A"

        q = q_template.format(cause=cause, mediator=mediator, effect=effect)
        ans = self._build_causal_explanation(views)
        return q, str(ans)

    def _apply_holistic_synthesis(
        self, q_template: str, views: list
    ) -> Tuple[str, str]:
        """
        Across all k charts, find the entity with the best composite performance.
        """
        cat = self._resolve_shared_cat(views)
        k = len(views)

        if not cat:
            return "No shared category column for holistic_synthesis", "N/A"

        q = q_template.format(k=k, cat=cat)
        ans = self._compute_composite_ranking(views, cat)
        return q, str(ans)

    # ── Answer computation helpers ────────────────────────────────────────────

    def _cross_rank_lookup(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        cat: str,
        m1: str,
        m2: str,
    ) -> str:
        """Return the rank of the top-m1 entity (from df_a) in df_b sorted by m2."""
        if df_a.empty or cat not in df_a.columns or m1 not in df_a.columns:
            return "N/A"
        top_entity = df_a.loc[df_a[m1].idxmax(), cat]
        if df_b.empty or cat not in df_b.columns or m2 not in df_b.columns:
            return "N/A"
        df_b_sorted = df_b.sort_values(m2, ascending=False).reset_index(drop=True)
        matches = df_b_sorted[df_b_sorted[cat] == top_entity]
        if matches.empty:
            return f"{top_entity} not found in Chart B"
        rank = int(matches.index[0]) + 1  # 1-indexed
        return f"{top_entity} (rank {rank} for {m2} in Chart B)"

    def _conditional_value_transfer(
        self,
        df_b: pd.DataFrame,
        entity: Any,
        cat: str,
        other_measure: str,
    ) -> str:
        """Look up entity in df_b and return its other_measure value."""
        if df_b.empty or cat not in df_b.columns or other_measure not in df_b.columns:
            return "N/A"
        row = df_b.loc[df_b[cat] == entity, other_measure]
        if row.empty:
            return f"{entity} not found in Chart B"
        return str(round(float(row.values[0]), 2))

    def _compare_trend_directions(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        entity_a: Any,
        entity_b: Any,
        cat: str,
        measure: str,
    ) -> str:
        """
        Compare whether entity_a and entity_b move in the same direction
        from Chart A to Chart B for the shared measure.
        """
        def _get_value(df: pd.DataFrame, entity: Any) -> Optional[float]:
            if cat not in df.columns or measure not in df.columns:
                return None
            row = df.loc[df[cat] == entity, measure]
            return float(row.values[0]) if not row.empty else None

        a1 = _get_value(df_a, entity_a)
        b1 = _get_value(df_b, entity_a)
        a2 = _get_value(df_a, entity_b)
        b2 = _get_value(df_b, entity_b)

        if any(v is None for v in [a1, b1, a2, b2]):
            return "Insufficient data to compare trends"

        dir_a = "up" if b1 > a1 else ("down" if b1 < a1 else "flat")
        dir_b = "up" if b2 > a2 else ("down" if b2 < a2 else "flat")

        same = dir_a == dir_b
        return (
            f"Yes — both {entity_a} and {entity_b} trend {dir_a} across both charts."
            if same
            else f"No — {entity_a} trends {dir_a} while {entity_b} trends {dir_b}."
        )

    def _identify_dominant_subcategory(
        self,
        df_b: pd.DataFrame,
        dominant_entity: Any,
        cat_col: str,
        measure: str,
    ) -> str:
        """
        In Chart B, find the sub-category most associated with the dominant entity.
        If cat_col is present in df_b, return the entity with highest measure
        (representing the most significant driver).
        """
        if df_b.empty or measure not in df_b.columns:
            return "N/A"
        # If the same cat column exists, narrow to the dominant entity's rows
        if cat_col in df_b.columns:
            subset = df_b[df_b[cat_col] == dominant_entity]
            if not subset.empty:
                return str(subset.loc[subset[measure].idxmax(), cat_col])
        # Otherwise return the entity with the highest measure across Chart B
        return str(df_b.loc[df_b[measure].idxmax(), df_b.columns[0]])

    def _verify_orthogonal_dominance(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        primary_cat: str,
        ortho_cat: str,
        measure: str,
    ) -> str:
        """
        Check if the top-performing primary_cat entity in df_a
        is also the highest-measure entity within each ortho_cat group in df_b.
        """
        if df_a.empty or primary_cat not in df_a.columns or measure not in df_a.columns:
            return "N/A"
        top_entity = df_a.loc[df_a[measure].idxmax(), primary_cat]

        if df_b.empty or ortho_cat not in df_b.columns or primary_cat not in df_b.columns or measure not in df_b.columns:
            return "N/A"

        groups = df_b[ortho_cat].unique()
        dominant_in_all = True
        not_dominant = []
        for grp in groups:
            subset = df_b[df_b[ortho_cat] == grp]
            if subset.empty:
                continue
            top_in_grp = subset.loc[subset[measure].idxmax(), primary_cat]
            if top_in_grp != top_entity:
                dominant_in_all = False
                not_dominant.append(str(grp))

        if dominant_in_all:
            return f"Yes — {top_entity} is the top {primary_cat} within every {ortho_cat} group."
        else:
            groups_str = ", ".join(not_dominant)
            return (
                f"No — {top_entity} is not dominant in {ortho_cat} group(s): {groups_str}."
            )

    def _build_causal_explanation(self, views: list) -> str:
        """
        Describe the direction of change in each of the 3 causal views
        and produce a narrative explanation.
        """
        directions = []
        for v in views:
            df = v.extracted_view
            m = v.measure
            if df is None or df.empty or not m or m not in df.columns:
                directions.append("unknown")
                continue
            series = pd.to_numeric(df[m], errors="coerce").dropna()
            if len(series) < 2:
                directions.append("flat")
            elif series.iloc[-1] > series.iloc[0]:
                directions.append("increased")
            elif series.iloc[-1] < series.iloc[0]:
                directions.append("decreased")
            else:
                directions.append("remained flat")

        cause_dir, med_dir, effect_dir = directions
        cause, mediator, effect = views[0].measure, views[1].measure, views[2].measure

        if cause_dir == "increased" and med_dir == "increased" and effect_dir == "decreased":
            return (
                f"Despite {cause} and {mediator} both increasing, {effect} decreased. "
                f"This may indicate a confounding variable, saturation effect, or a lag "
                f"in how {mediator} translates to {effect}."
            )
        return (
            f"{cause} {cause_dir}, {mediator} {med_dir}, and {effect} {effect_dir}. "
            f"The relationship between these metrics warrants further investigation."
        )

    def _compute_composite_ranking(self, views: list, cat: str) -> str:
        """
        Rank entities by their average z-score across all view measures.
        Returns the entity with the highest composite score.
        """
        # Collect per-entity scores from each view
        score_frames = []
        for v in views:
            df = v.extracted_view
            m = v.measure
            if df is None or df.empty or not m or cat not in df.columns or m not in df.columns:
                continue
            tmp = df[[cat, m]].copy()
            col_std = tmp[m].std()
            col_mean = tmp[m].mean()
            if col_std == 0:
                tmp["z"] = 0.0
            else:
                tmp["z"] = (tmp[m] - col_mean) / col_std
            score_frames.append(tmp[[cat, "z"]].rename(columns={"z": f"z_{m}"}))

        if not score_frames:
            return "N/A"

        # Merge all score frames on cat
        merged = score_frames[0]
        for sf in score_frames[1:]:
            merged = merged.merge(sf, on=cat, how="outer")

        z_cols = [c for c in merged.columns if c.startswith("z_")]
        merged["composite"] = merged[z_cols].mean(axis=1)
        best = merged.loc[merged["composite"].idxmax(), cat]
        return str(best)

    def _resolve_shared_cat(self, views: list) -> Optional[str]:
        """Find a category column shared across the given views."""
        if not views:
            return None
        group_sets = [set(v.group_by) for v in views if v.group_by]
        if not group_sets:
            return views[0].binding.get("cat") or views[0].binding.get("cat1")
        shared = group_sets[0].intersection(*group_sets[1:])
        if shared:
            for col in views[0].group_by:
                if col in shared:
                    return col
        return views[0].group_by[0] if views[0].group_by else None
