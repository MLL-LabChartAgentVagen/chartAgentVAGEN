"""Tests for Dashboard — run standalone or via run_all.py.

    python tests/dashboard/test_dashboard.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tests.conftest import make_bar_spec, make_line_spec, make_scatter_spec
from dashboard import Dashboard


def _make_two_view_dashboard(**kwargs) -> Dashboard:
    v1 = make_bar_spec()
    v2 = make_bar_spec()
    v2.score = 1.0
    return Dashboard(views=[v1, v2], relationship="comparative",
                     pattern="same_type_compare", **kwargs)


class TestDashboardScore(unittest.TestCase):

    def test_score_is_mean_of_views(self):
        v1 = make_bar_spec(); v1.score = 4.0
        v2 = make_bar_spec(); v2.score = 2.0
        d = Dashboard(views=[v1, v2], relationship="comparative")
        self.assertAlmostEqual(d.score, 3.0)

    def test_score_empty_views(self):
        d = Dashboard(views=[], relationship="test")
        self.assertEqual(d.score, 0.0)


class TestDashboardFamilyDiversity(unittest.TestCase):

    def test_same_family_diversity_one(self):
        """Two Comparison views → diversity = 1."""
        v1, v2 = make_bar_spec(), make_bar_spec()
        d = Dashboard(views=[v1, v2], relationship="dual_metric")
        self.assertEqual(d.family_diversity, 1)

    def test_different_family_diversity(self):
        """Bar (Comparison) + Line (Trend) → diversity = 2."""
        v1 = make_bar_spec()
        v2 = make_line_spec()
        d = Dashboard(views=[v1, v2], relationship="mixed")
        self.assertEqual(d.family_diversity, 2)


class TestDashboardViewCount(unittest.TestCase):

    def test_view_count(self):
        d = _make_two_view_dashboard()
        self.assertEqual(d.view_count, 2)


class TestDashboardMeasures(unittest.TestCase):

    def test_measures_unique_and_ordered(self):
        v1 = make_bar_spec(); v1.score = 2.0   # measure = revenue
        v2 = make_bar_spec(); v2.score = 1.5   # measure = revenue (duplicate)
        d = Dashboard(views=[v1, v2], relationship="dual_metric")
        # revenue should appear only once
        self.assertEqual(d.measures.count("revenue"), 1)

    def test_measures_insertion_order(self):
        v1 = make_line_spec()   # measure = revenue (via binding m1 fallback? no — line uses measure slot)
        v2 = make_scatter_spec()  # measure = cost (m1)
        d = Dashboard(views=[v1, v2], relationship="mixed")
        # First measure should match first view's measure
        self.assertEqual(d.measures[0], v1.measure)


class TestDashboardAutoDerive(unittest.TestCase):

    def test_auto_title_when_none(self):
        d = _make_two_view_dashboard()
        self.assertIsNotNone(d.title)
        self.assertIn("comparative".replace("_", " ").title(), d.title)

    def test_explicit_title_preserved(self):
        d = _make_two_view_dashboard(title="My Dashboard")
        self.assertEqual(d.title, "My Dashboard")

    def test_layout_two_views(self):
        d = _make_two_view_dashboard()
        self.assertEqual(d.layout, "2x1")

    def test_layout_three_views(self):
        v1, v2, v3 = make_bar_spec(), make_bar_spec(), make_bar_spec()
        d = Dashboard(views=[v1, v2, v3], relationship="causal_chain")
        self.assertEqual(d.layout, "1x3")

    def test_layout_four_views(self):
        views = [make_bar_spec() for _ in range(4)]
        d = Dashboard(views=views, relationship="mixed")
        self.assertEqual(d.layout, "2x2")

    def test_explicit_layout_preserved(self):
        d = _make_two_view_dashboard(layout="1x2")
        self.assertEqual(d.layout, "1x2")


class TestDashboardQAPairs(unittest.TestCase):

    def test_add_qa_appends(self):
        d = _make_two_view_dashboard()
        qa = {"question": "Q?", "answer": "A", "difficulty": "easy"}
        d.add_qa(qa)
        self.assertEqual(len(d.qa_pairs), 1)
        self.assertEqual(d.qa_pairs[0]["question"], "Q?")

    def test_qa_pairs_start_empty(self):
        d = _make_two_view_dashboard()
        self.assertEqual(d.qa_pairs, [])


class TestDashboardSerialisation(unittest.TestCase):

    def test_to_dict_required_keys(self):
        d = _make_two_view_dashboard()
        data = d.to_dict()
        required = {"pattern", "relationship", "title", "layout",
                    "score", "family_diversity", "measures", "views", "qa_pairs"}
        self.assertTrue(required.issubset(data.keys()))

    def test_to_dict_views_have_chart_type(self):
        d = _make_two_view_dashboard()
        for v_dict in d.to_dict()["views"]:
            self.assertIn("chart_type", v_dict)

    def test_summary_contains_pattern_and_relationship(self):
        d = _make_two_view_dashboard()
        summary = d.summary()
        self.assertIn("same_type_compare", summary)
        self.assertIn("comparative", summary)


if __name__ == "__main__":
    unittest.main()
