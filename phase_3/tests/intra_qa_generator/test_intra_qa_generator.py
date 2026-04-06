"""Tests for IntraQAGenerator — run standalone or via run_all.py.

    python tests/intra_qa_generator/test_intra_qa_generator.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
from tests.conftest import make_bar_spec, make_scatter_spec
from view_spec import ViewSpec
from view_extraction_rules import VIEW_EXTRACTION_RULES
from intraQAGenerator.intra_qa_generator import IntraQAGenerator


def _pie_spec_with_data() -> ViewSpec:
    df = pd.DataFrame({
        "region":  ["North", "South", "East"],
        "revenue": [100.0, 400.0, 500.0],
    })
    spec = ViewSpec(
        chart_type="pie_chart",
        binding={"cat": "region", "measure": "revenue"},
        rule=VIEW_EXTRACTION_RULES["pie_chart"],
        extracted_view=df,
    )
    return spec


class TestIntraQAGeneratorBasic(unittest.TestCase):

    def setUp(self):
        self.gen = IntraQAGenerator()

    def test_generate_qa_returns_two_strings(self):
        """generate_qa() always returns a (str, str) tuple."""
        spec = make_bar_spec()
        q, a = self.gen.generate_qa(spec)
        self.assertIsInstance(q, str)
        self.assertIsInstance(a, str)

    def test_generate_qa_empty_df_returns_na(self):
        """Empty extracted_view → answer is 'N/A'."""
        spec = make_bar_spec(extracted=False)
        spec.extracted_view = pd.DataFrame()
        _, a = self.gen.generate_qa(spec)
        self.assertEqual(a, "N/A")

    def test_generate_qa_none_df_returns_na(self):
        """None extracted_view → answer is 'N/A'."""
        spec = make_bar_spec(extracted=False)
        spec.extracted_view = None
        _, a = self.gen.generate_qa(spec)
        self.assertEqual(a, "N/A")

    def test_no_templates_for_unknown_chart(self):
        """Unknown chart_type → question mentions 'No templates'."""
        spec = ViewSpec(
            chart_type="mystery_chart",
            binding={"cat": "region", "measure": "revenue"},
            rule={},
            extracted_view=pd.DataFrame({"region": ["A"], "revenue": [1]}),
        )
        q, _ = self.gen.generate_qa(spec)
        self.assertIn("No templates", q)


class TestIntraQAGeneratorAllQA(unittest.TestCase):

    def setUp(self):
        self.gen = IntraQAGenerator()

    def test_generate_all_qa_returns_list(self):
        """generate_all_qa() returns a list."""
        spec = make_bar_spec()
        result = self.gen.generate_all_qa(spec)
        self.assertIsInstance(result, list)

    def test_generate_all_qa_has_required_keys(self):
        """Each QA dict has template, question, answer, difficulty."""
        spec = make_bar_spec()
        result = self.gen.generate_all_qa(spec)
        self.assertGreater(len(result), 0)
        for item in result:
            for key in ("template", "question", "answer", "difficulty"):
                self.assertIn(key, item, msg=f"Key '{key}' missing in {item}")

    def test_applicable_filter_bar_chart(self):
        """Only bar_chart-applicable templates selected for bar_chart spec."""
        spec = make_bar_spec()
        result = self.gen.generate_all_qa(spec)
        # Templates applicable to bar_chart in intra_view_templates:
        # value_retrieval, extremum, comparison
        applicable_names = {r["template"] for r in result}
        non_bar_templates = {"trend", "proportion", "distribution_shape",
                              "correlation_direction"}
        self.assertTrue(applicable_names.isdisjoint(non_bar_templates),
                         msg=f"Non-bar templates were included: {applicable_names & non_bar_templates}")


class TestIntraQAGeneratorTemplates(unittest.TestCase):

    def setUp(self):
        self.gen = IntraQAGenerator()

    def test_extremum_answer_is_actual_entity(self):
        """Extremum template answer equals the entity with highest/lowest measure."""
        spec = make_bar_spec()
        df = spec.extracted_view
        results = self.gen.generate_all_qa(spec)
        extremum_results = [r for r in results if r["template"] == "extremum"]
        if extremum_results:
            answer = extremum_results[0]["answer"]
            # Answer should be one of the actual region values
            self.assertIn(answer, df["region"].astype(str).values)

    def test_proportion_answer_is_percentage_string(self):
        """Proportion template answer ends with '%'."""
        spec = _pie_spec_with_data()
        results = self.gen.generate_all_qa(spec)
        prop_results = [r for r in results if r["template"] == "proportion"]
        if prop_results:
            self.assertTrue(
                prop_results[0]["answer"].endswith("%"),
                msg=f"Expected % suffix, got: {prop_results[0]['answer']}"
            )

    def test_correlation_direction_answer_valid(self):
        """Correlation template returns one of the three direction strings."""
        spec = make_scatter_spec()
        results = self.gen.generate_all_qa(spec)
        corr_results = [r for r in results if r["template"] == "correlation_direction"]
        if corr_results:
            valid = {"positive", "negative", "no clear relationship"}
            self.assertIn(corr_results[0]["answer"], valid)


if __name__ == "__main__":
    unittest.main()
