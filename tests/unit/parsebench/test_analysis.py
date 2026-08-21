"""The program's half of the analysis: the parts that decide what the reports say.

Three models' answers only become comparable through code -- what counts as the same
reading, what counts as a right prediction, which form a failure took, how a sample
drawn per form is weighted back to the run. Those four are checked here, on made-up
answers, because on real ones a wrong rule looks like a disagreement between models.
"""

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "parsebench" / "tools"))

from analysis.rules import Rule, keys_agree              # noqa: E402
from analysis.tally import (Answers, Item, _value_axes, agreement,      # noqa: E402
                            density_band, map_back, quantities)
from contract.format import FORMS, MECHANISM_STEP, STEPS  # noqa: E402
from failures.forms import _missing_labels               # noqa: E402
from failures.mechanisms import _weighted                # noqa: E402
from failures.tables import Page, numbers                # noqa: E402
from report import numbers as reconcile                  # noqa: E402
from report.crops import figure_boxes, figure_index      # noqa: E402


def rule(value="42.3", labels=("Mercy General", "Surgery")):
    return Rule("id", "stem", value, labels, 0, 0.05, ())


class TestPredictedKeysAreGraded:
    """The one quantity the annotation can settle: the values were given, the
    labels were withheld, so the predicted key set is a prediction."""

    def test_containment_counts_either_way(self):
        """The benchmark itself matches a label to a cell by containment, so a
        prediction that is longer or shorter than the label is still right."""
        assert keys_agree(["Mercy General Hospital", "Surgery"], ("Mercy General", "Surgery"))
        assert keys_agree(["Mercy", "Surgery"], ("Mercy General", "Surgery"))
        assert not keys_agree(["Riverside", "Surgery"], ("Mercy General", "Surgery"))

    def test_a_missing_key_is_wrong_even_when_the_rest_match(self):
        assert not keys_agree(["Mercy General"], ("Mercy General", "Surgery"))

    def test_extra_keys_do_not_make_it_wrong(self):
        assert keys_agree(["Mercy General", "Surgery", "2024"], ("Mercy General", "Surgery"))


class TestAgreementClasses:
    def test_three_saying_the_same_thing_is_unanimous(self):
        assert Item("p", "u", {"a": "bar", "b": "bar", "c": "bar"}).klass == "unanimous"

    def test_two_and_one_silent_is_majority(self):
        assert Item("p", "u", {"a": "bar", "b": "bar", "c": None}).klass == "majority"

    def test_two_models_both_answering_is_unanimous(self):
        """The classes are relative to how many were asked -- the repeat control
        compares one model against itself, and two is all there is."""
        assert Item("p", "u", {"a": "bar", "b": "bar"}).klass == "unanimous"

    def test_one_alone_is_single(self):
        assert Item("p", "u", {"a": "bar", "b": None, "c": None}).klass == "single"

    def test_two_saying_different_things_is_a_conflict_not_a_majority(self):
        """Silence and a different answer are not the same thing: one is a model
        that did not look, the other is a model that disagrees."""
        assert Item("p", "u", {"a": "bar", "b": "line", "c": None}).klass == "conflict"

    def test_the_rate_is_averaged_over_pages_not_over_items(self):
        """The benchmark averages per page, so a page with many components cannot
        outweigh a page with few."""
        items = [Item("p1", "a", {"m": 1, "n": 1, "o": 1}),
                 Item("p1", "b", {"m": 1, "n": 1, "o": 1}),
                 Item("p2", "c", {"m": 1, "n": None, "o": None})]
        assert agreement(items)["rate"] == pytest.approx(0.5)


class TestFiguresAreAlignedByReadingOrder:
    def _answers(self, first, second):
        answers = Answers(["m1", "m2"], [{"stem": "p", "document": "d", "tags": "",
                                          "rules": 0}])
        answers.records["p"] = {"m1": {"answer": {"figures": first}},
                                "m2": {"answer": {"figures": second}}}
        return answers

    def figure(self, **kwargs):
        return {"id": "f", "type": "bar", "type_other": "", "panels": 1, "series": 1,
                "categories": 4, "marks": 12, "values_printed": "none",
                "heading": {"figure_number": "", "title": "", "subtitle": "",
                            "unit_text": "", "placement": "above"}, **kwargs}

    def test_a_model_seeing_fewer_figures_is_silent_not_wrong(self):
        answers = self._answers([self.figure(), self.figure()], [self.figure()])
        types = quantities(answers)["图表类型判定"]
        assert [item.klass for item in types] == ["unanimous", "single"]

    def test_an_unreadable_entry_is_not_a_figure(self):
        """`unreadable` is how a model says an entry is not a chart at all, so it
        must not shift every later figure's position."""
        answers = self._answers([self.figure(type="unreadable"), self.figure()],
                                [self.figure()])
        assert len(quantities(answers)["图表类型判定"]) == 1

    def test_other_is_compared_on_the_name_it_was_given(self):
        answers = self._answers([self.figure(type="other", type_other="Dumbbell")],
                                [self.figure(type="other", type_other="dumbbell")])
        assert quantities(answers)["图表类型判定"][0].klass == "unanimous"

    def test_density_is_compared_by_band_not_by_count(self):
        answers = self._answers([self.figure(marks=21)], [self.figure(marks=59)])
        assert quantities(answers)["稠密度档"][0].klass == "unanimous"
        assert density_band(21) == "21–60"

    def test_the_heading_is_compared_on_number_and_placement_only(self):
        """`format.NOT_ALIGNED`: comparing the title text compares transcription."""
        left = self.figure(heading={"figure_number": "Figure 3", "title": "Wait times",
                                    "subtitle": "", "unit_text": "", "placement": "above"})
        right = self.figure(heading={"figure_number": "Fig. 3", "title": "ER waits",
                                     "subtitle": "", "unit_text": "", "placement": "above"})
        assert quantities(self._answers([left], [right]))["标题"][0].klass == "unanimous"


class TestFailureForms:
    def test_the_metric_names_the_labels_it_could_not_associate(self):
        explanation = ("Value at (1, 2) missing labels: ['ride sharing', 'global']; "
                       "Value at (3, 1) missing labels: ['global']")
        assert _missing_labels(explanation) == ["global"]

    def test_every_form_and_mechanism_maps_into_the_four_step_judgement(self):
        assert set(FORMS) >= {"label_unlinked", "value_off", "no_table"}
        for mechanism, step in MECHANISM_STEP.items():
            assert step in STEPS or step == 0, mechanism

    def test_a_comma_is_read_both_ways_because_the_metric_reads_it_both_ways(self):
        assert numbers("1,5") == pytest.approx([1.5, 15.0], abs=1e-9) or \
               sorted(numbers("1,5")) == pytest.approx([1.5, 15.0])

    def test_a_table_is_found_in_pipe_markdown_and_in_html(self):
        page = Page.build("p", "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
                             "<table><tr><td>x</td></tr><tr><td>y</td></tr></table>")
        assert len(page.tables) == 2


class TestWeightingBackToTheRun:
    """The sample is equal-sized per form, so a count inside it is a count within a
    form. Weighting is what turns it into a statement about the run."""

    def test_a_rare_form_does_not_count_as_much_as_a_common_one(self):
        from collections import Counter
        by_form = {"label_unlinked": Counter({"key_off_the_value_row": 10}),
                   "value_absent": Counter({"figure_not_transcribed": 10})}
        sampled = Counter({"label_unlinked": 10, "value_absent": 10})
        # Patched in by the caller in production; here the counts come from the file.
        weighted = _weighted(by_form, sampled, failures=896)
        assert weighted["key_off_the_value_row"][1] > weighted["figure_not_transcribed"][1]


class TestNumbersCited:
    def test_a_number_the_program_computed_is_found(self):
        entries = [reconcile.Entry(72.2, "形态表 / 寻址失败合计")]
        rows = reconcile.reconcile([{"claim": "寻址失败", "value": "72.2%", "source": "形态表"}],
                                   entries)
        assert rows[0]["found"] and "寻址" in rows[0]["where"]

    def test_a_fraction_and_a_percentage_are_the_same_claim(self):
        entries = [reconcile.Entry(72.2, "形态表 / 寻址失败合计")]
        assert reconcile.reconcile([{"claim": "x", "value": "0.722", "source": ""}],
                                   entries)[0]["found"]

    def test_a_number_nobody_computed_is_recorded_as_missing_not_corrected(self):
        rows = reconcile.reconcile([{"claim": "x", "value": "88%", "source": "自己数的"}],
                                   [reconcile.Entry(72.2, "形态表")])
        assert rows[0]["found"] is False and rows[0]["value"] == "88%"

    def test_a_small_integer_being_found_is_not_evidence(self):
        """With a few hundred small integers in the tables, `7` is somewhere
        whatever it was supposed to count."""
        rows = reconcile.reconcile([{"claim": "卡在第 3 步的页数", "value": "7", "source": ""},
                                    {"claim": "定位键命中率", "value": "74.3%", "source": ""}],
                                   [reconcile.Entry(7, "组件表 / 页数"),
                                    reconcile.Entry(74.3, "判分表 / 命中率")])
        assert rows[0]["decisive"] is False
        assert rows[1]["decisive"] is True and rows[1]["found"]

    def test_the_cell_named_beside_a_claim_is_the_one_sharing_its_words(self):
        entries = [reconcile.Entry(60.0, "组件表 `hgrid_only` / 页数"),
                   reconcile.Entry(60.0, "一致率表 卡在哪一步 / rate")]
        rows = reconcile.reconcile([{"claim": "卡在哪一步的三家一致率", "value": "60.0%",
                                     "source": ""}], entries)
        assert "卡在哪一步" in rows[0]["where"]


class TestAddressedCell:
    """Which cell counts as `what the parser wrote for this value`."""

    def test_a_key_that_is_a_number_is_not_read_back_as_the_value(self):
        """A year is a key and a number at once. The intersection of its own row
        and its own column is the key cell, and reading it back would turn a key
        into a misread value."""
        from failures.forms import addressed_cells, _label_cells
        from failures.tables import Page

        page = Page.build("p", "| Year | Month | Surplus |\n|---|---|---|\n"
                               "| 2024 | Sep | $80B |\n| 2025 | Oct | $50B |")
        rule = Rule("id", "p", "100", ("2024", "Sep"), 0, 0.1, ())
        readings = {round(value) for *_, value in
                    addressed_cells(rule, page, _label_cells(rule, page))}
        assert 2024 not in readings


class TestVocabularyControl:
    def test_a_free_name_maps_back_when_it_shares_two_stem_words(self):
        assert map_back("wrapped_category_labels") == "wrapped_category_labels"

    def test_a_name_with_nothing_in_common_stays_unmapped(self):
        """The residual is the point of the control, so it must not be mapped away."""
        assert map_back("zzz_qqq") is None


class TestParallelValueAxes:
    """Two value axes matter only when they are parallel.

    A scatter plot measures a quantity on both x and y and is not ambiguous. A left
    and a right value axis are: one pixel height on that panel means two different
    numbers, which is what the recorded value has no field for.
    """

    @staticmethod
    def figure(*sides_and_roles):
        return {"axes": [{"side": side, "role": role} for side, role in sides_and_roles]}

    def test_a_scatter_is_not_a_dual_axis_figure(self):
        assert _value_axes(self.figure(("left", "value"), ("bottom", "value"))) == 1

    def test_a_left_and_a_right_value_axis_are(self):
        assert _value_axes(self.figure(("left", "value"), ("right", "value"),
                                       ("bottom", "category"))) == 2

    def test_a_plain_bar_chart_has_one(self):
        assert _value_axes(self.figure(("left", "value"), ("bottom", "category"))) == 1

    def test_a_pie_has_none(self):
        assert _value_axes({"axes": []}) == 0

    def test_small_multiples_listing_one_left_axis_per_panel_are_not_dual(self):
        """Fifteen panels, each with its own left axis, is one side, not fifteen."""
        panels = self.figure(*([("left", "value")] * 15), ("bottom", "time"))
        assert _value_axes(panels) == 1


class TestFigureCrops:
    """The report cuts a figure out of the page rather than showing the whole page.

    The boxes come from the parser's own layout blocks, and are used only to decide
    where to cut a picture for a human. Nothing counted anywhere depends on them, but
    a box outside the page would silently produce a blank picture.
    """

    def test_boxes_are_fractions_of_the_page_in_reading_order(self):
        page = ROOT / "parsebench/data/runs/ppdoclayoutv3_lean_qwen/chart/2025-EIS_p41.raw.json"
        if not page.exists():
            pytest.skip("the parser run is not checked in")
        boxes = figure_boxes("2025-EIS_p41")
        assert boxes, "a page with a chart block has at least one figure box"
        for box in boxes:
            assert 0 <= box.x0 < box.x1 <= 1
            assert 0 <= box.y0 < box.y1 <= 1

    def test_a_figure_id_names_the_figure_it_reads(self):
        assert figure_index("f1") == 0
        assert figure_index("f3") == 2
        assert figure_index("page") == 0          # a page-level claim shows the first


class TestEveryNumberInTheReportHasASource:
    """The agent writes prose and the program writes numbers, and this is the seam.

    Every number in `view_text` is a named hole filled from `data/stats/`. A hole the
    facts table does not produce would ship as a `{placeholder}` in the page, or stop
    the build -- which is the point, but only if the two files agree about the names.
    """

    @staticmethod
    def holes():
        import re
        source = (ROOT / "parsebench/tools/report/view_text.py").read_text(encoding="utf-8")
        # Digits belong in the name class: `p10_table_n` is a hole like any other,
        # and leaving them out made this check silently skip every hole with one.
        return set(re.findall(r"\{([a-z_][a-z_0-9]*)\}", source))

    def test_the_facts_table_produces_every_hole(self):
        facts_source = (ROOT / "parsebench/tools/report/view.py").read_text(encoding="utf-8")
        produced = set(re.findall(r'"([a-z_][a-z_0-9]*)":', facts_source))
        missing = self.holes() - produced
        assert not missing, f"no fact behind {sorted(missing)}"
