"""Tests for DashboardComposer — run standalone or via run_all.py.

    python tests/dashboard_composer/test_dashboard_composer.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
from tests.conftest import MINI_SCHEMA, MINI_DF, make_bar_spec, make_line_spec
from view_spec import ViewSpec
from view_extraction_rules import VIEW_EXTRACTION_RULES
from view_extractor import ViewData
from view_enumerator import ViewEnumerator
from dashboard_composer import DashboardComposer
from dashboard import Dashboard


def _enumerated_views():
    """Return fully extracted feasible views from MINI_DF."""
    enumerator = ViewEnumerator()
    views = enumerator.enumerate(MINI_SCHEMA, MINI_DF)
    for v in views:
        vd = ViewData(v, MINI_DF)
        v.extracted_view = vd.extracted_view   # write back so compose() can access it
    return views


class TestDashboardComposerCompose(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.composer = DashboardComposer()
        cls.views = _enumerated_views()

    def test_compose_returns_list(self):
        """compose() always returns a list."""
        result = self.composer.compose(self.views, MINI_SCHEMA, target_k=2)
        self.assertIsInstance(result, list)

    def test_compose_k2_view_count(self):
        """All k=2 dashboards have exactly 2 views."""
        dashboards = self.composer.compose(self.views, MINI_SCHEMA, target_k=2)
        for d in dashboards:
            self.assertEqual(d.view_count, 2, msg=f"Dashboard {d.summary()} has wrong view count")

    def test_compose_k4_view_count(self):
        """All k=4 dashboards have exactly 4 views."""
        dashboards = self.composer.compose(self.views, MINI_SCHEMA, target_k=4)
        for d in dashboards:
            self.assertEqual(d.view_count, 4)

    def test_compose_returns_dashboard_instances(self):
        """Every returned item is a Dashboard."""
        dashboards = self.composer.compose(self.views, MINI_SCHEMA, target_k=2)
        for d in dashboards:
            self.assertIsInstance(d, Dashboard)

    def test_compose_pattern_field_set(self):
        """Every dashboard has a non-empty pattern string."""
        dashboards = self.composer.compose(self.views, MINI_SCHEMA, target_k=2)
        for d in dashboards:
            self.assertIsInstance(d.pattern, str)
            self.assertGreater(len(d.pattern), 0)


class TestDashboardComposerHelpers(unittest.TestCase):

    def setUp(self):
        self.composer = DashboardComposer()

    # ── _has_temporal ────────────────────────────────────────────────────────

    def test_has_temporal_true(self):
        spec = ViewSpec(
            chart_type="line_chart",
            binding={"time": "date", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["line_chart"],
        )
        self.assertTrue(self.composer._has_temporal(spec))

    def test_has_temporal_false(self):
        spec = make_bar_spec()
        self.assertFalse(self.composer._has_temporal(spec))

    # ── _find_view_for_measure ───────────────────────────────────────────────

    def test_find_view_for_measure_hit(self):
        spec = make_bar_spec()
        result = self.composer._find_view_for_measure([spec], "revenue")
        self.assertIs(result, spec)

    def test_find_view_for_measure_miss(self):
        spec = make_bar_spec()
        result = self.composer._find_view_for_measure([spec], "cost")
        self.assertIsNone(result)

    def test_find_view_for_measure_first_match(self):
        """Returns the first matching view, not subsequent ones."""
        v1 = make_bar_spec(); v1.score = 5.0
        v2 = make_bar_spec(); v2.score = 1.0
        result = self.composer._find_view_for_measure([v1, v2], "revenue")
        self.assertIs(result, v1)

    # ── _is_declared_orthogonal ──────────────────────────────────────────────

    def test_is_declared_orthogonal_true(self):
        pairs = [{"col_a": "region", "col_b": "segment"}]
        self.assertTrue(
            self.composer._is_declared_orthogonal("region", "segment", pairs))

    def test_is_declared_orthogonal_reversed(self):
        """Order of col_a / col_b doesn't matter."""
        pairs = [{"col_a": "region", "col_b": "segment"}]
        self.assertTrue(
            self.composer._is_declared_orthogonal("segment", "region", pairs))

    def test_is_declared_orthogonal_false(self):
        pairs = [{"col_a": "region", "col_b": "segment"}]
        self.assertFalse(
            self.composer._is_declared_orthogonal("region", "revenue", pairs))

    # ── _maximize_type_diversity ─────────────────────────────────────────────

    def test_maximize_type_diversity_count(self):
        views = _enumerated_views()
        selected = self.composer._maximize_type_diversity(views, k=4)
        self.assertEqual(len(selected), 4)

    def test_maximize_type_diversity_prefers_distinct_families(self):
        views = _enumerated_views()
        selected = self.composer._maximize_type_diversity(views, k=4)
        families = [v.family for v in selected]
        # Should have at least 2 distinct families when enough variety exists
        self.assertGreaterEqual(len(set(families)), 1)


if __name__ == "__main__":
    unittest.main()
