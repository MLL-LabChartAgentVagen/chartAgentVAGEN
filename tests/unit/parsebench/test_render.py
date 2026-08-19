"""The two documents: one page's report, and the index over all of them."""

import json

import pytest
from conftest import component

import markdown
from checks import Finding
from index import (countable_figures, generality, pick_examples, render_index,
                   summary_json, triage)
from vocabulary import VOCABULARY
from report import render_report, write_report
from rules import Rule
from viewer import render_viewer, write_assets
from schema import STEPS


class TestRenderReport:
    def test_all_six_sections_are_present(self, result):
        page = result(rules=[Rule("42.3", ("Mercy General",), 0.05, 0)], attribution=["f1"])
        text = render_report(page)
        assert [f"## {n} · " in text for n in range(1, 7)] == [True] * 6

    def test_the_ours_column_comes_from_the_vocabulary_not_the_page(self, result, analysis):
        page = result(analysis=analysis(components=["reference_line"]))
        assert "| `reference_line` | 参考线（水平/垂直虚线，含零线，常带独立图例项） " \
               "| f1 | **无** | the words on the page |" in render_report(page)

    def test_a_component_is_printed_with_the_evidence_written_for_it(self, result, analysis):
        page = result(analysis=analysis(
            components=[component("reference_line", evidence="dashed rule at 100")]))
        assert "dashed rule at 100" in render_report(page)

    def test_the_rule_and_the_prediction_share_one_row(self, result, analysis):
        page = result(rules=[Rule("42.3", ("Mercy General",), 0.05, 0)], attribution=["f1"],
                      analysis=analysis(spot_checks=[{
                          "value": "42.3", "figure_id": "f1", "mark": "the tallest bar",
                          "printed_on_figure": False,
                          "addressing_keys": ["Mercy General"]}]))
        row = next(l for l in render_report(page).splitlines() if l.startswith("| 1 | 42.3"))
        assert "the tallest bar" in row and "`Mercy General`" in row

    def test_the_heading_is_printed_split_with_where_it_sits(self, result, analysis, figure,
                                                             heading):
        page = result(analysis=analysis(figures=[figure(heading=heading(
            subtitle="US property, 2011 = 100", unit_text="2011 = 100", placement="beside"))]))
        text = render_report(page)
        assert "US property, 2011 = 100" in text and "[与图并排]" in text

    def test_an_unnamed_other_type_is_printed_as_the_hole_it_is(self, result, analysis, figure):
        page = result(analysis=analysis(figures=[figure(type="other", type_other="dumbbell")]))
        assert "`other · dumbbell`" in render_report(page)

    def test_an_unattributed_rule_is_marked_in_the_table(self, result):
        page = result(rules=[Rule("1", ("x",), 0.05, 0)], attribution=[None])
        assert "| 未归属 |" in render_report(page)

    def test_a_pipe_in_a_heading_does_not_break_the_table(self, result, analysis, figure,
                                                          heading):
        page = result(analysis=analysis(figures=[figure(heading=heading(title="a | b"))]))
        assert "a \\| b" in render_report(page)

    def test_a_finding_is_written_out_in_full(self, result):
        page = result(findings=[Finding("keys_missing", "rules need 3 keys")])
        assert markdown.FINDING_ZH["keys_missing"] in render_report(page)


def test_every_label_map_covers_what_the_code_emits():
    emitted = {"no_figures", "keys_missing", "unattributed_rules",
               "estimate_tag_but_values_printed", "no_estimate_tag_but_values_absent",
               "estimate_tag_but_every_value_printed", "dense_not_flagged",
               "dense_flagged_without_marks", "reasked_after_an_empty_answer",
               "component_without_the_layout_it_needs", "component_on_an_unknown_figure",
               "component_without_evidence", "panel_names_count_mismatch",
               "series_names_count_mismatch", "spot_check_count_mismatch",
               "values_not_placed", "addressing_keys_wrong", "other_type_unnamed"}
    assert emitted <= set(markdown.FINDING_ZH)
    assert set(STEPS) == set(markdown.STEP_ZH)


class TestCountableFigures:
    def test_an_entry_the_model_ruled_out_is_not_a_figure(self, result, analysis, figure):
        page = result(analysis=analysis(
            figures=[figure(id="f1"), figure(id="f2", type="other", marks=0)],
            unreadable=[{"figure_id": "f2", "reason": "装饰色块"}]))
        assert [f["id"] for f in countable_figures(page)] == ["f1"]

    def test_it_is_kept_out_of_the_type_mix(self, result, analysis, figure):
        page = result(analysis=analysis(
            figures=[figure(id="f1", type="bar"), figure(id="f2", type="other")],
            unreadable=[{"figure_id": "f2", "reason": "占位"}]))
        summary = summary_json([page], "m")
        assert summary["chart_types"] == {"bar": 1} and summary["figures"] == 1


class TestGenerality:
    """Document spread, not page count, is what separates a convention from a habit."""

    def test_pages_spread_over_many_documents_read_as_general(self):
        from collections import Counter
        spread = Counter({f"doc{i}": 1 for i in range(20)})
        assert generality(20, spread, 70)[0] == "通用"

    def test_pages_piled_into_one_document_read_as_concentrated(self):
        from collections import Counter
        assert generality(20, Counter({"doc": 18, "other": 2}), 70)[0] == "集中"

    def test_a_frequent_component_is_not_concentrated_by_construction(self):
        """145 pages out of a 70-document sample can never touch 145 documents."""
        from collections import Counter
        spread = Counter({f"doc{i}": 2 for i in range(63)})
        assert generality(145, spread, 70)[0] == "通用"

    def test_too_few_pages_gets_no_verdict(self):
        from collections import Counter
        assert generality(2, Counter({"a": 1, "b": 1}), 70)[0] == "样本不足"


class TestTriage:
    """Three lists, two measured tests, every gap in exactly one of them."""

    def spread(self, result, analysis, key, n, docs):
        return [result(stem=f"p{i}", document=f"d{i % docs}",
                       analysis=analysis(components=[key])) for i in range(n)]

    def keys(self, pages, bucket):
        return [c.key for c, *_ in triage(pages)[bucket]]

    def test_something_the_metric_can_see_is_kept_for_the_score(self, result, analysis):
        pages = self.spread(result, analysis, "no_value_axis", 20, 20)
        assert "no_value_axis" in self.keys(pages, "keep_score")

    def test_a_widespread_construction_the_metric_ignores_is_kept_for_diversity(
            self, result, analysis):
        pages = self.spread(result, analysis, "unit_in_axis_or_title", 20, 20)
        assert self.keys(pages, "keep_diversity") == ["unit_in_axis_or_title"]
        assert "unit_in_axis_or_title" not in self.keys(pages, "keep_score")

    def test_one_publishers_habit_the_metric_ignores_is_dropped(self, result, analysis):
        """One document out of 20 possible is 0.05 -- well clear of the held-back band."""
        pages = self.spread(result, analysis, "unit_in_axis_or_title", 20, 1) + \
            [result(stem=f"q{i}", document=f"e{i}", analysis=analysis(components=[]))
             for i in range(60)]
        assert "unit_in_axis_or_title" in self.keys(pages, "drop")
        assert "unit_in_axis_or_title" not in self.keys(pages, "keep_diversity")

    def test_something_that_never_appears_is_undecided_not_dropped(self, result, analysis):
        """`no_value_axis` blocks step 2 -- but this sample cannot say how often."""
        pages = self.spread(result, analysis, "reference_line", 20, 20)
        assert "no_value_axis" in self.keys(pages, "undecided")

    def test_too_few_pages_is_held_back_rather_than_called_a_house_style(
            self, result, analysis):
        """`error_bars` on two pages is "cannot tell", not "one publisher's habit"."""
        pages = self.spread(result, analysis, "error_bars", 2, 2) + \
            [result(stem=f"q{i}", document=f"e{i}", analysis=analysis(components=[]))
             for i in range(60)]
        assert "error_bars" in self.keys(pages, "undecided")
        assert "error_bars" not in self.keys(pages, "drop")

    def test_a_spread_sitting_on_the_cut_is_held_back(self, result, analysis):
        """20 pages over 9 documents is 0.45 -- the threshold, not the data, decides."""
        pages = self.spread(result, analysis, "unit_in_axis_or_title", 20, 9) + \
            [result(stem=f"q{i}", document=f"e{i}", analysis=analysis(components=[]))
             for i in range(60)]
        assert "unit_in_axis_or_title" in self.keys(pages, "undecided")

    def test_something_we_can_already_draw_is_in_no_list(self, result, analysis):
        pages = self.spread(result, analysis, "grouped_bar", 20, 20)
        assert all("grouped_bar" not in self.keys(pages, b) for b in triage(pages))

    def test_every_gap_lands_in_exactly_one_list(self, result, analysis):
        pages = self.spread(result, analysis, "reference_line", 20, 20)
        lists = triage(pages)
        keys = [c.key for b in lists for c, *_ in lists[b]]
        assert len(keys) == len(set(keys)) == sum(not c.ours for c in VOCABULARY)

    def test_the_gap_item_comes_out_of_the_components_own_basis(self, result, analysis):
        pages = self.spread(result, analysis, "negative_values", 20, 20)
        row = next(r for r in triage(pages)["keep_score"] if r[0].key == "negative_values")
        assert row[4] == "P6"


class TestRenderIndex:
    def pages(self, result, analysis):
        return [result(stem=f"doc_p{i}", document=f"doc{i}",
                       analysis=analysis(components=["reference_line"])) for i in range(24)] + \
               [result(stem=f"doc_p{i}", document=f"doc{i}", analysis=analysis(components=[]))
                for i in range(24, 48)]

    def test_a_gap_row_carries_its_band_count_reason_and_an_example(self, result, analysis):
        text = render_index(self.pages(result, analysis), "m")
        row = next(l for l in text.splitlines() if l.startswith("| 高 | `reference_line`"))
        assert "24（50%）" in row
        assert "chart_types.md` 无此形状" in row
        assert "/report.md)" in row

    def test_a_gap_row_prints_the_evidence_the_model_wrote(self, result, analysis):
        pages = [result(stem="p1", document="d1", analysis=analysis(
            components=[component("reference_line", evidence="dashed rule at 100")]))]
        assert "dashed rule at 100" in render_index(pages, "m")

    def test_a_type_the_condition_table_lacks_is_listed_as_a_gap(self, result, analysis, figure):
        pages = [result(stem="p1", document="d1", analysis=analysis(
            figures=[figure(type="map")]))]
        text = render_index(pages, "m")
        assert "### 1.3 类型缺口" in text
        assert any(l.startswith("| `map` |") for l in text.splitlines())

    def test_a_type_we_can_draw_is_not_a_gap(self, result, analysis, figure):
        """The mix belongs to the portrait; only what we cannot draw is a gap."""
        pages = [result(stem="p1", document="d1", analysis=analysis(figures=[figure(type="bar")]))]
        text = render_index(pages, "m")
        gap_table = text.split("### 1.3 类型缺口")[1].split("`other` 这一格")[0]
        assert "| `bar` |" not in gap_table
        assert "| `bar` | 1 |" in text.split("### 2.2 类型配比")[1]

    def test_what_we_lack_is_listed_before_what_we_have(self, result, analysis):
        text = render_index(self.pages(result, analysis), "m")
        assert text.index("| `reference_line` |") < text.index("| `grouped_bar` |")

    def test_the_summary_counts_the_same_pages(self, result, analysis):
        summary = summary_json(self.pages(result, analysis), "m")
        assert summary["pages"] == 48 and summary["component_pages"]["reference_line"] == 24
        assert summary["component_share"]["reference_line"] == 0.5
        assert summary["component_documents"]["reference_line"] == 24

    def test_a_new_component_is_counted_by_page(self, result, analysis):
        pages = [result(stem=f"p{i}", analysis=analysis(
            new_components=[{"name": "dot_plot", "figure_id": "f1", "evidence": "dots",
                             "why_it_matters": "点图"}])) for i in range(3)]
        assert "| `dot_plot` | 3 | ✓ |" in render_index(pages, "m")

    def test_a_name_seen_once_is_folded_away_rather_than_listed_as_a_row(self, result, analysis):
        pages = [result(stem="p1", analysis=analysis(
            new_components=[{"name": "dot_plot", "figure_id": "f1", "evidence": "dots",
                             "why_it_matters": "点图"}]))]
        text = render_index(pages, "m")
        assert "只出现在 1 页的 1 个" in text and "| `dot_plot` | 1 |" not in text

    def test_the_names_given_to_other_figures_are_collected(self, result, analysis, figure):
        pages = [result(stem="p1", analysis=analysis(
            figures=[figure(type="other", type_other="Dumbbell")]))]
        assert "`dumbbell`" in render_index(pages, "m")

    def test_a_table_or_a_placeholder_is_sorted_out_of_the_type_gap(self, result, analysis,
                                                                    figure):
        """Only the third bucket is a family the condition table lacks."""
        from index import bucketed_types
        from collections import Counter
        buckets = bucketed_types(Counter({"data table": 7, "placeholder ignore": 2,
                                          "dumbbell range plot": 1}))
        assert [(t, [n for n, _ in m]) for t, _, m in buckets] == [
            ("表格", ["data table"]), ("不是图", ["placeholder ignore"]),
            ("图形", ["dumbbell range plot"])]

    def test_a_stem_with_parentheses_stays_one_link(self, result, analysis):
        """`(` inside a markdown target closes it early, so it is percent-encoded."""
        pages = [result(stem="(Web)_p1", analysis=analysis(components=["reference_line"]))]
        assert "](pages/%28Web%29_p1/report.md)" in render_index(pages, "m")


class TestPickExamples:
    def test_the_longest_evidence_wins(self, result, analysis):
        thin = result(stem="a_thin", analysis=analysis(
            components=[component("reference_line", evidence="a line")]))
        rich = result(stem="z_rich", analysis=analysis(
            components=[component("reference_line", evidence="a dashed rule at the 100 mark")]))
        picked = pick_examples([thin, rich], ["reference_line"])
        assert picked["reference_line"][0].stem == "z_rich"

    def test_one_page_does_not_become_the_example_for_everything(self, result, analysis):
        """The old rule sent every key to the same simple page. Spread is the fix."""
        keys = ["reference_line", "error_bars", "broken_axis"]
        pages = [result(stem=f"p{i}", analysis=analysis(components=keys)) for i in range(3)]
        leads = {k: v[0].stem for k, v in pick_examples(pages, keys).items()}
        assert len(set(leads.values())) == 3

    def test_a_component_nobody_showed_has_no_example(self, result, analysis):
        assert pick_examples([result(analysis=analysis(components=[]))],
                             ["reference_line"])["reference_line"] == []


class TestRenderViewer:
    def pages(self, result, analysis):
        return [result(stem=f"doc_p{i}", document=f"doc{i}",
                       analysis=analysis(components=["reference_line"])) for i in range(3)]

    def test_the_markup_closes_every_tag_it_opens(self, result, analysis):
        html = render_viewer(self.pages(result, analysis), "m")
        for tag in ("section", "article", "div", "table", "figure", "p"):
            assert html.count(f"<{tag}") == html.count(f"</{tag}>"), tag

    def test_every_tab_button_has_a_panel(self, result, analysis):
        html = render_viewer(self.pages(result, analysis), "m")
        import re
        buttons = set(re.findall(r'<button data-tab="([a-z]+)"', html))
        panels = set(re.findall(r'<section id="([a-z]+)" role="tabpanel"', html))
        assert buttons == panels == {"order", "portrait", "trust"}

    def test_the_build_list_splits_on_whether_the_metric_can_see_it(self, result, analysis):
        """A component the four steps never look at cannot raise the score."""
        from index import triage
        pages = [result(stem=f"p{i}", document=f"d{i}",
                        analysis=analysis(components=["unit_in_axis_or_title", "no_value_axis"]))
                 for i in range(20)]
        lists = triage(pages)
        assert [c.key for c, *_ in lists["keep_score"]] == ["no_value_axis"]
        assert [c.key for c, *_ in lists["keep_diversity"]] == ["unit_in_axis_or_title"]

    def test_a_gap_card_shows_the_page_it_was_counted_on(self, result, analysis):
        html = render_viewer(self.pages(result, analysis), "m")
        assert "参考线" in html and 'src="assets/doc_p0.jpg"' in html

    def test_a_gap_card_prints_the_evidence(self, result, analysis):
        pages = [result(stem="p1", document="d", analysis=analysis(
            components=[component("reference_line", evidence="dashed rule at 100")]))]
        assert "dashed rule at 100" in render_viewer(pages, "m")

    def test_a_type_gap_gets_a_card_of_its_own(self, result, analysis, figure):
        pages = [result(stem="p1", document="d", analysis=analysis(figures=[figure(type="map")]))]
        html = render_viewer(pages, "m")
        assert "类型缺口" in html and "<code>map</code>" in html

    def test_the_page_script_parses(self, result, analysis, tmp_path):
        """`SCRIPT` is a plain string, so a `\n` in it reaches the page as a newline.

        Inside a JS string literal that is a syntax error, and the whole page goes
        inert -- tabs stop switching, the contents list never gets built. Nothing
        else in these tests would notice.
        """
        import re
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            pytest.skip("node is not installed")
        html = render_viewer(self.pages(result, analysis), "m")
        script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
        path = tmp_path / "viewer.js"
        path.write_text(script, encoding="utf-8")
        done = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr

    def test_every_tab_has_headings_for_the_contents_list(self, result, analysis):
        """The contents list is built from the sections' own headings, at load time."""
        import re
        html = render_viewer(self.pages(result, analysis), "m")
        for body in re.findall(r'<section id="[a-z]+" role="tabpanel".*?</section>',
                               html, re.S):
            assert 'h3 class="band"' in body

    def test_no_image_points_above_the_page(self, result, analysis):
        """A preview pane or a static server will not serve `../`."""
        html = render_viewer(self.pages(result, analysis), "m")
        assert 'src="../' not in html and 'href="../' not in html

    def test_without_assets_it_falls_back_to_the_rendered_pages(self, result, analysis):
        html = render_viewer(self.pages(result, analysis), "m", assets=False)
        assert 'src="../data/pages/doc_p0.png"' in html

    def test_every_colour_is_defined_on_bare_root(self, result, analysis):
        """A token defined only inside a media query never applies in the default theme."""
        html = render_viewer(self.pages(result, analysis), "m")
        base = html[html.index(":root{"):html.index("@media")]
        used = {t for t in ("--ground", "--surface", "--raised", "--ink", "--muted",
                            "--line", "--gap", "--have", "--shadow")}
        assert all(f"{token}:" in base for token in used)

    def test_a_stem_with_parentheses_is_url_encoded(self, result, analysis):
        pages = [result(stem="(Web)_p1", analysis=analysis(components=["reference_line"]))]
        assert "assets/%28Web%29_p1.jpg" in render_viewer(pages, "m")


class TestWriteReport:
    def paths(self, tmp_path):
        pages_dir = tmp_path / "parsebench" / "data" / "pages"
        pages_dir.mkdir(parents=True)
        (pages_dir / "doc_p1.png").write_bytes(b"png")
        return pages_dir, tmp_path / "parsebench" / "reports" / "doc_p1"

    def test_it_writes_the_three_files_and_links_the_page(self, tmp_path, result):
        pages_dir, directory = self.paths(tmp_path)
        write_report(directory, result(), pages_dir / "doc_p1.png")
        assert (directory / "report.md").exists()
        assert json.loads((directory / "analysis.json").read_text())["stem"] == "doc_p1"
        assert (directory / "page.png").is_symlink()
        assert (directory / "page.png").read_bytes() == b"png"

    def test_writing_twice_replaces_the_link(self, tmp_path, result):
        pages_dir, directory = self.paths(tmp_path)
        write_report(directory, result(), pages_dir / "doc_p1.png")
        write_report(directory, result(), pages_dir / "doc_p1.png")
        assert (directory / "page.png").is_symlink()


class TestWriteAssets:
    def test_it_downscales_each_page_beside_the_viewer(self, tmp_path, result):
        pytest.importorskip("PIL")
        from PIL import Image
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()
        Image.new("RGB", (1241, 1654), "white").save(pages_dir / "doc_p1.png")
        assert write_assets([result()], tmp_path / "reports", pages_dir) is True
        written = tmp_path / "reports" / "assets" / "doc_p1.jpg"
        assert written.exists() and Image.open(written).width == 800

    def test_a_page_without_a_raster_is_skipped_rather_than_raising(self, tmp_path, result):
        pytest.importorskip("PIL")
        assert write_assets([result()], tmp_path / "reports", tmp_path / "absent") is True
