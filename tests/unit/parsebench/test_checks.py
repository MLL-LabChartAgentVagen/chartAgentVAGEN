"""What the program says about the answer: against itself, and against the rules."""

from conftest import component

from checks import Finding, crosscheck, evidence_of, keys_of, reconcile
from rules import Rule


class TestReconcile:
    def test_an_across_panel_key_is_dropped_when_there_is_one_panel(self, analysis):
        subject = analysis(components=["shared_legend", "stacked_bar"])
        findings = reconcile(subject)
        assert keys_of(subject) == ["stacked_bar"]
        assert findings[0].code == "component_without_the_layout_it_needs"

    def test_it_survives_when_the_panels_are_there(self, analysis, figure):
        subject = analysis(components=["shared_legend"],
                           figures=[figure(panels=3, panel_names=["a", "b", "c"])])
        assert reconcile(subject) == []
        assert keys_of(subject) == ["shared_legend"]

    def test_multi_figure_page_needs_a_second_figure(self, analysis):
        subject = analysis(components=["multi_figure_page"])
        reconcile(subject)
        assert keys_of(subject) == []

    def test_a_component_hung_on_a_figure_that_is_not_there_is_reported(self, analysis):
        subject = analysis(components=[component("stacked_bar", figure_id="f9")])
        assert [f.code for f in reconcile(subject)] == ["component_on_an_unknown_figure"]

    def test_a_component_with_no_evidence_is_reported(self, analysis):
        subject = analysis(components=[component("stacked_bar", evidence="")])
        assert [f.code for f in reconcile(subject)] == ["component_without_evidence"]

    def test_page_is_a_place_a_component_may_sit(self, analysis):
        subject = analysis(components=[component("multi_figure_page", figure_id="page")])
        assert "component_on_an_unknown_figure" not in [f.code for f in reconcile(subject)]


class TestKeys:
    def test_a_key_outside_the_vocabulary_is_not_counted(self, analysis):
        assert keys_of(analysis(components=[component("invented_key")])) == []

    def test_the_evidence_is_the_one_written_for_that_key(self, analysis):
        subject = analysis(components=[component("stacked_bar", evidence="four segments")])
        assert evidence_of(subject, "stacked_bar") == "four segments"


class TestCrosscheck:
    def codes(self, subject, rules=(), tags="untagged", attribution=()) -> list[str]:
        return [f.code for f in crosscheck(subject, list(rules), tags, list(attribution))]

    def test_a_three_key_rule_against_a_flat_figure(self, analysis):
        rules = [Rule("1", ("a", "b", "c"), 0.05, 0)]
        assert "keys_missing" in self.codes(analysis(), rules=rules, attribution=["f1"])

    def test_three_keys_are_available_with_panels_and_series(self, analysis, figure):
        subject = analysis(figures=[figure(panels=2, panel_names=["a", "b"],
                                           series=2, series_names=["s", "t"])])
        rules = [Rule("1", ("a", "b", "c"), 0.05, 0)]
        assert "keys_missing" not in self.codes(subject, rules=rules, attribution=["f1"])

    def test_the_estimate_tag_contradicts_printed_values(self, analysis, figure):
        subject = analysis(figures=[figure(values_printed="all")])
        assert "estimate_tag_but_values_printed" in self.codes(subject, tags="need_estimate")

    def test_the_untagged_group_contradicts_unprinted_values(self, analysis):
        assert "no_estimate_tag_but_values_absent" in self.codes(analysis())

    def test_an_unattributed_rule_is_reported(self, analysis):
        assert "unattributed_rules" in self.codes(analysis(), attribution=["f1", None])

    def test_a_dense_figure_must_carry_the_density_key(self, analysis, figure):
        subject = analysis(figures=[figure(marks=352)])
        assert "dense_not_flagged" in self.codes(subject)

    def test_an_other_type_must_be_named(self, analysis, figure):
        subject = analysis(figures=[figure(type="other", type_other="")])
        assert "other_type_unnamed" in self.codes(subject)

    def test_a_clean_page_produces_nothing(self, analysis):
        subject = analysis(spot_checks=[{"value": "1", "figure_id": "f1", "mark": "the bar",
                                         "printed_on_figure": False, "addressing_keys": ["a"]}])
        assert self.codes(subject, rules=[Rule("1", ("a",), 0.05, 0)],
                          attribution=["f1"], tags="need_estimate") == []


class TestSpotChecks:
    """The one place a claim is graded. The model saw the values, never the labels."""

    def check(self, **kw) -> dict:
        base = {"value": "42.3", "figure_id": "f1", "mark": "the Mercy General bar",
                "printed_on_figure": False, "addressing_keys": ["Mercy General"]}
        return {**base, **kw}

    def codes(self, subject, rules, tags="need_estimate") -> list[str]:
        return [f.code for f in crosscheck(subject, list(rules), tags, ["f1"] * len(rules))]

    def test_a_prediction_that_covers_the_rule_labels_passes(self, analysis):
        subject = analysis(spot_checks=[self.check()])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0)]
        assert "addressing_keys_wrong" not in self.codes(subject, rules)

    def test_a_longer_prediction_still_covers_a_shorter_label(self, analysis):
        subject = analysis(spot_checks=[self.check(addressing_keys=["Mercy General Hospital"])])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0)]
        assert "addressing_keys_wrong" not in self.codes(subject, rules)

    def test_a_missed_label_is_graded_wrong(self, analysis):
        subject = analysis(spot_checks=[self.check(addressing_keys=["Surgery"])])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0)]
        assert "addressing_keys_wrong" in self.codes(subject, rules)

    def test_a_value_the_model_could_not_place_is_reported_not_graded(self, analysis):
        subject = analysis(spot_checks=[self.check(figure_id="not_found", addressing_keys=[])])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0)]
        codes = self.codes(subject, rules)
        assert "values_not_placed" in codes and "addressing_keys_wrong" not in codes

    def test_answering_a_different_number_of_values_is_reported(self, analysis):
        subject = analysis(spot_checks=[self.check()])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0), Rule("35.8", ("St. Luke's",), 0.05, 0)]
        assert "spot_check_count_mismatch" in self.codes(subject, rules)

    def test_the_estimate_tag_contradicts_every_value_being_printed(self, analysis):
        subject = analysis(spot_checks=[self.check(printed_on_figure=True)])
        rules = [Rule("42.3", ("Mercy General",), 0.05, 0)]
        assert "estimate_tag_but_every_value_printed" in self.codes(subject, rules)


def test_a_finding_is_two_strings():
    finding = Finding("keys_missing", "rules need 3 keys")
    assert (finding.code, finding.detail) == ("keys_missing", "rules need 3 keys")
