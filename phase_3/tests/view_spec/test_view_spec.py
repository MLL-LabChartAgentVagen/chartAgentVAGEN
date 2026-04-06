"""Tests for ViewSpec — run standalone or via run_all.py.

    python tests/view_spec/test_view_spec.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
from tests.conftest import MINI_DF, make_bar_spec
from view_spec import ViewSpec, CHART_FAMILIES
from view_extraction_rules import VIEW_EXTRACTION_RULES


class TestViewSpecProperties(unittest.TestCase):

    def test_family_mapping(self):
        """family property returns correct string for known chart types."""
        for chart_type, expected_family in CHART_FAMILIES.items():
            spec = ViewSpec(
                chart_type=chart_type,
                binding={"measure": "revenue"},
                rule={},
            )
            self.assertEqual(spec.family, expected_family)

    def test_family_unknown(self):
        """family returns 'Unknown' for unrecognised chart type."""
        spec = ViewSpec(chart_type="mystery_chart", binding={}, rule={})
        self.assertEqual(spec.family, "Unknown")

    def test_measure_primary(self):
        """measure returns binding['measure'] when present."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule={},
        )
        self.assertEqual(spec.measure, "revenue")

    def test_measure_fallback_m1(self):
        """measure falls back to binding['m1'] when 'measure' is absent."""
        spec = ViewSpec(
            chart_type="scatter_plot",
            binding={"m1": "cost", "m2": "revenue"},
            rule={},
        )
        self.assertEqual(spec.measure, "cost")

    def test_measure_empty(self):
        """measure returns empty string when no measure binding exists."""
        spec = ViewSpec(chart_type="bar_chart", binding={}, rule={})
        self.assertEqual(spec.measure, "")

    def test_group_by_collects_slots(self):
        """group_by returns all recognised group slots from binding."""
        spec = ViewSpec(
            chart_type="line_chart",
            binding={"time": "date", "series": "region", "measure": "revenue"},
            rule={},
        )
        self.assertIn("date", spec.group_by)
        self.assertIn("region", spec.group_by)

    def test_group_by_no_duplicates(self):
        """group_by never contains duplicate column names."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "cat1": "region", "measure": "revenue"},
            rule={},
        )
        self.assertEqual(len(spec.group_by), len(set(spec.group_by)))

    def test_group_key_is_sorted_tuple(self):
        """group_key is a sorted tuple for stable comparison."""
        spec = ViewSpec(
            chart_type="line_chart",
            binding={"time": "date", "series": "region", "measure": "revenue"},
            rule={},
        )
        gk = spec.group_key
        self.assertIsInstance(gk, tuple)
        self.assertEqual(list(gk), sorted(gk))

    def test_select_columns_unique(self):
        """select_columns contains no duplicates."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "region"},   # deliberate overlap
            rule={},
        )
        cols = spec.select_columns
        self.assertEqual(len(cols), len(set(cols)))

    def test_with_filter_sets_filter(self):
        """with_filter() sets filter when none previously existed."""
        spec = make_bar_spec()
        new_spec = spec.with_filter("revenue > 100")
        self.assertEqual(new_spec.filter, "revenue > 100")
        self.assertIsNone(spec.filter)   # original unchanged

    def test_with_filter_compounds(self):
        """with_filter() wraps both filters in parens when one already exists."""
        spec = make_bar_spec()
        spec2 = spec.with_filter("revenue > 100")
        spec3 = spec2.with_filter("region == 'North'")
        self.assertIn("revenue > 100", spec3.filter)
        self.assertIn("region == 'North'", spec3.filter)
        self.assertTrue(spec3.filter.startswith("("))

    def test_extract_view_shape(self):
        """extract_view() returns a DataFrame with the correct columns."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["bar_chart"],
        )
        df = spec.extract_view(MINI_DF)
        self.assertIn("region", df.columns)
        self.assertIn("revenue", df.columns)
        self.assertGreater(len(df), 0)


if __name__ == "__main__":
    unittest.main()
