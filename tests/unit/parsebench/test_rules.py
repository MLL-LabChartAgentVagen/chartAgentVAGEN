"""Loading the spot-check rules, and deciding which figure each one addresses."""

import json

import pytest
from rules import Rule, attribute, load_rules


class TestLoadRules:
    def test_rules_are_grouped_by_page_stem(self, tmp_path):
        jsonl = tmp_path / "chart.jsonl"
        jsonl.write_text(
            json.dumps({"pdf": "docs/chart/a_p1.pdf", "tags": [],
                        "rule": json.dumps({"value": "1", "labels": ["x"], "max_diffs": 0})}) + "\n"
            + json.dumps({"pdf": "docs/chart/a_p1.pdf", "tags": [],
                          "rule": json.dumps({"value": "2", "labels": ["y"],
                                              "relative_tolerance": 0.05})}) + "\n"
            + json.dumps({"pdf": "docs/chart/b_p9.pdf", "tags": [],
                          "rule": json.dumps({"value": "3", "labels": []})}) + "\n")
        rules = load_rules(jsonl)
        assert sorted(rules) == ["a_p1", "b_p9"]
        assert [r.value for r in rules["a_p1"]] == ["1", "2"]

    def test_a_missing_tolerance_is_the_documented_default(self, tmp_path):
        jsonl = tmp_path / "chart.jsonl"
        jsonl.write_text(json.dumps({"pdf": "a_p1.pdf", "tags": [],
                                     "rule": json.dumps({"value": "1", "labels": ["x"]})}))
        assert load_rules(jsonl)["a_p1"][0].tolerance == 0.01


class TestAttribution:
    RULES = [Rule("1", ("Surgery", "Mercy General"), 0.05, 0),
             Rule("2", ("Berlin",), 0.05, 0),
             Rule("3", ("nothing on the page",), 0.05, 0)]

    def test_one_figure_takes_every_rule(self, figure):
        assert attribute(self.RULES, [figure()]) == ["f1", "f1", "f1"]

    def test_labels_pick_the_figure_that_prints_them(self, figure):
        figures = [figure(id="f1", caption="ER waits", category_names=["Surgery", "Peds"],
                          series_names=["Mercy General"]),
                   figure(id="f2", caption="Europe", category_names=["Berlin", "Paris"])]
        assert attribute(self.RULES, figures) == ["f1", "f2", None]

    def test_matching_ignores_case_and_punctuation(self, figure):
        figures = [figure(id="f1", category_names=["not it"]),
                   figure(id="f2", category_names=["st. luke's"])]
        assert attribute([Rule("1", ("St Lukes",), 0.05, 0)], figures) == ["f2"]


@pytest.mark.parametrize("labels,arity", [((), 0), (("a",), 1), (("a", "b", "c"), 3)])
def test_arity_is_the_number_of_keys_a_value_needs(labels, arity):
    assert Rule("1", labels, 0.01, 0).arity == arity
