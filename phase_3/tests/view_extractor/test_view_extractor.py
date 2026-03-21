"""Tests for ViewExtractor and ViewData — run standalone or via run_all.py.

    python tests/view_extractor/test_view_extractor.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
from tests.conftest import MINI_DF, make_bar_spec, make_line_spec
from view_spec import ViewSpec
from view_extractor import ViewExtractor, ViewData
from view_extraction_rules import VIEW_EXTRACTION_RULES


class TestViewExtractor(unittest.TestCase):

    def _make_extractor(self, chart_type="bar_chart",
                        binding=None) -> ViewExtractor:
        if binding is None:
            binding = {"cat": "region", "measure": "revenue"}
        spec = ViewSpec(
            chart_type=chart_type,
            binding=binding,
            rule=VIEW_EXTRACTION_RULES[chart_type],
        )
        return ViewExtractor(spec)

    def test_extract_view_returns_dataframe(self):
        """extract_view() always returns a DataFrame."""
        extractor = self._make_extractor()
        result = extractor.extract_view(MINI_DF)
        self.assertIsInstance(result, pd.DataFrame)

    def test_extract_view_correct_columns(self):
        """Extracted view contains exactly the binding columns."""
        extractor = self._make_extractor()
        result = extractor.extract_view(MINI_DF)
        self.assertIn("region", result.columns)
        self.assertIn("revenue", result.columns)

    def test_extract_view_filter_reduces_rows(self):
        """Adding a filter to the spec reduces the row count."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["bar_chart"],
            filter="region == 'North'",
        )
        extractor = ViewExtractor(spec)
        result = extractor.extract_view(MINI_DF)
        self.assertLess(len(result), len(MINI_DF))

    def test_extract_view_groupby_reduces_rows(self):
        """Group-by spec produces one row per unique category value."""
        extractor = self._make_extractor()
        result = extractor.extract_view(MINI_DF)
        n_cats = MINI_DF["region"].nunique()
        self.assertEqual(len(result), n_cats)


class TestViewData(unittest.TestCase):

    def test_viewdata_populates_extracted_view(self):
        """ViewData constructor sets extracted_view on the spec."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["bar_chart"],
        )
        vd = ViewData(spec, MINI_DF)
        self.assertIsNotNone(vd.extracted_view)
        self.assertIsInstance(vd.extracted_view, pd.DataFrame)

    def test_viewdata_stores_references(self):
        """ViewData exposes view_spec and master_table."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["bar_chart"],
        )
        vd = ViewData(spec, MINI_DF)
        self.assertIs(vd.view_spec, spec)
        self.assertIs(vd.master_table, MINI_DF)

    def test_viewdata_groupby_aggregates(self):
        """ViewData extracted_view has one row per grouping value."""
        spec = ViewSpec(
            chart_type="bar_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["bar_chart"],
        )
        vd = ViewData(spec, MINI_DF)
        expected_rows = MINI_DF["region"].nunique()
        self.assertEqual(len(vd.extracted_view), expected_rows)

    def test_viewdata_time_series_spec_has_time_col(self):
        """Line chart ViewData result contains the time binding column."""
        spec = ViewSpec(
            chart_type="line_chart",
            binding={"time": "date", "series": "region", "measure": "revenue"},
            rule=VIEW_EXTRACTION_RULES["line_chart"],
        )
        vd = ViewData(spec, MINI_DF)
        self.assertIn("date", vd.extracted_view.columns)


if __name__ == "__main__":
    unittest.main()
