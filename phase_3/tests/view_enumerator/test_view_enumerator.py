"""Tests for ViewEnumerator — run standalone or via run_all.py.

    python tests/view_enumerator/test_view_enumerator.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tests.conftest import MINI_SCHEMA, MINI_DF
from view_enumerator import ViewEnumerator
from view_spec import ViewSpec


class TestViewEnumerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.enumerator = ViewEnumerator()
        cls.views = cls.enumerator.enumerate(MINI_SCHEMA, MINI_DF)

    def test_enumerate_returns_list(self):
        """enumerate() returns a non-empty list."""
        self.assertIsInstance(self.views, list)
        self.assertGreater(len(self.views), 0)

    def test_all_items_are_view_specs(self):
        """Every item in the result is a ViewSpec."""
        for v in self.views:
            self.assertIsInstance(v, ViewSpec)

    def test_results_sorted_by_score_descending(self):
        """Scores are in descending order."""
        scores = [v.score for v in self.views]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_all_specs_have_chart_type(self):
        """Every spec has a non-empty chart_type string."""
        for v in self.views:
            self.assertIsInstance(v.chart_type, str)
            self.assertGreater(len(v.chart_type), 0)

    def test_score_nonnegative(self):
        """All scores are >= 0."""
        for v in self.views:
            self.assertGreaterEqual(v.score, 0)

    def test_group_columns_by_role(self):
        """_group_columns_by_role maps measure, temporal, and categorical roles correctly."""
        groups = self.enumerator._group_columns_by_role(MINI_SCHEMA)
        self.assertIn("measure", groups)
        self.assertIn("revenue", groups["measure"])
        self.assertIn("temporal", groups)
        self.assertIn("date", groups["temporal"])
        self.assertIn("primary", groups)
        self.assertIn("region", groups["primary"])


if __name__ == "__main__":
    unittest.main()
