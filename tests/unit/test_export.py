"""Turning records into training targets, and checking an answer without ground truth."""

import json
from dataclasses import replace

import pytest

from chartgen.common.geometry import Box
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec, TextBlock
from chartgen.registry import channels
from chartgen.s02_figure.project import project
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default
from chartgen.s04_record.selfcheck import finish
from chartgen.s05_output import export as E
from chartgen.s05_output import verify as V

UNITS = {"wait_minutes": "minutes", "cost": "USD", "satisfaction": "points"}


@pytest.fixture(scope="module")
def tables(er):
    import json
    from pathlib import Path

    from chartgen.config import Config
    from chartgen.s01_data.author import compose as compose_data

    payload = json.loads((Path(__file__).resolve().parents[1] / "samples" /
                          "funnel_scenario.json").read_text(encoding="utf-8"))
    return {"er": er,
            "checkout": compose_data(payload, scenario_id="checkout", seed=20260816,
                                     config=Config.load())}


@pytest.fixture(scope="module")
def record(er_table, er_schema, tmp_path_factory):
    binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", key_sources=("axis_tick",))
    view = project(er_table.df, binding, er_schema)
    spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),), column_units=UNITS,
                      caption="Average wait by hospital, to assess the triage policy.")
    return finish(render(spec, default(), tmp_path_factory.mktemp("ex")), spec)


@pytest.fixture(scope="module")
def titled(er_table, er_schema, tmp_path_factory):
    """A figure carrying the text a real batch draws on it: a number, a title, a unit.

    The page document names each table by what is drawn on the image, so a fixture
    with nothing written on it cannot exercise that.
    """
    binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", key_sources=("axis_tick",))
    view = project(er_table.df, binding, er_schema)
    spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),), column_units=UNITS,
                      caption="Average wait by hospital, to assess the triage policy.",
                      texts=(TextBlock("figure_number", "Figure 3", "figure", "above"),
                             TextBlock("title", "Wait times by hospital", "figure", "above"),
                             TextBlock("unit", "minutes", "figure", "above")))
    return finish(render(spec, default(), tmp_path_factory.mktemp("ti")), spec)


@pytest.fixture(scope="module")
def panelled(er_table, er_schema, tmp_path_factory):
    """Two panels, each titled, which is where a panel name can enter a key."""
    binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                      aggregate="AVG", key_sources=("axis_tick",))
    view = project(er_table.df, binding, er_schema)
    spec = FigureSpec("f02", "er", (
        PanelSpec("p0", (view,), (TextBlock("title", "First half", "panel", "above"),)),
        PanelSpec("p1", (view,), (TextBlock("title", "Second half", "panel", "above"),)),
    ), layout="side_by_side", column_units=UNITS)
    return finish(render(spec, default(), tmp_path_factory.mktemp("ex2")), spec)


class TestOneRowManyTargets:
    def test_every_mark_is_in_the_grounded_table(self, record):
        targets = E.build(record)
        assert len(targets.grounded_table) == len(record.marks)
        row = targets.grounded_table[0]
        assert set(row) == {"key", "values", "box", "rows", "readable", "labeled"}

    def test_the_spot_check_asks_only_for_values_that_can_be_read(self, record):
        targets = E.build(record)
        assert targets.spot_check and len(targets.spot_check) <= E.SPOT_CHECKS
        assert all(e["tolerance"] == pytest.approx(0.01) for e in targets.spot_check)

        # With half the marks unreadable, half the spot checks go.
        half = replace(record, marks=tuple(
            replace(m, readable=(i % 2 == 0)) for i, m in enumerate(record.marks)))
        asked = {tuple(e["key"]) for e in E.build(half).spot_check}
        assert asked == {m.key for m in half.marks if m.readable}
        assert all(not m.readable or m.key in asked for m in half.marks)

    def test_nothing_is_asked_for_when_nothing_can_be_read(self, record):
        blind = replace(record, marks=tuple(replace(m, readable=False)
                                            for m in record.marks))
        targets = E.build(blind)
        assert targets.spot_check == [] and targets.mark_read == []
        assert len(targets.mark_locate) == len(record.marks)

    def test_a_written_value_is_asked_for_as_it_was_written(self, er_table, er_schema,
                                                            tmp_path):
        """The label is the answer, down to how it reads. Compared as a number that
        means the rounding the printing did and nothing more: the unrounded value is
        nowhere on the page, so asking for it would mark the only readable answer
        wrong, and anything wider would accept a value the label rules out."""
        binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="AVG", key_sources=("axis_tick",))
        view = project(er_table.df, binding, er_schema)
        spec = FigureSpec("f03", "er", (PanelSpec("p0", (view,)),), column_units=UNITS)
        out = render(spec, replace(default(), value_labels="all", decimals=0), tmp_path)
        targets = E.build(finish(out, spec))
        assert targets.spot_check
        for entry in targets.spot_check:
            printed = float(entry["printed"].replace(",", ""))
            slack = entry["tolerance"] * abs(entry["value"])
            assert abs(printed - entry["value"]) <= slack + 1e-9
            assert slack <= 0.5 + 1e-6        # written to whole numbers

    def test_an_estimated_value_keeps_the_benchmark_tolerance(self, er_table, er_schema,
                                                              tmp_path):
        binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="AVG", key_sources=("axis_tick",))
        view = project(er_table.df, binding, er_schema)
        spec = FigureSpec("f04", "er", (PanelSpec("p0", (view,)),), column_units=UNITS)
        out = render(spec, replace(default(), value_labels="none"), tmp_path)
        targets = E.build(finish(out, spec))
        assert targets.spot_check
        assert all("printed" not in e and e["tolerance"] == channels.RELATIVE_TOLERANCE
                   for e in targets.spot_check)

    def test_localisation_keeps_the_marks_whose_value_was_dropped(self, record):
        blinded = replace(record, marks=tuple(
            replace(m, readable=False) for m in record.marks))
        targets = E.build(blinded)
        assert len(targets.mark_locate) == len(record.marks)
        assert targets.mark_read == []

    def test_drilldown_answers_with_the_row_count(self, record):
        targets = E.build(record)
        assert sum(e["rows"] for e in targets.drilldown) == 900

    def test_the_caption_reaches_the_target_as_the_record_carries_it(self, record):
        """What the caption says is `caption.py`'s business and is tested there. What
        this checks is that the exporter hands over the record's, not a rebuilt one."""
        assert E.build(record).caption == record.caption and record.caption

    def test_where_each_segment_of_the_key_was_read_from_is_its_own_target(self, record):
        targets = E.build(record)
        assert all(len(e["key"]) == len(e["sources"]) for e in targets.key_source)
        assert {s for e in targets.key_source for s in e["sources"]} == {"axis_tick"}


class TestKeyScope:
    def test_the_narrow_scope_names_only_what_is_inside_the_plotting_area(self, panelled):
        keys = [tuple(r["key"]) for r in E.build(panelled, key_scope="mark").grounded_table]
        assert keys[0] == ("Mercy General",)

    def test_the_panel_scope_puts_the_panel_name_in_front(self, panelled):
        rows = E.build(panelled, key_scope="panel").grounded_table
        assert tuple(rows[0]["key"]) == ("First half", "Mercy General")
        assert tuple(rows[-1]["key"]) == ("Second half", "Riverside")

    def test_the_panel_name_is_the_text_that_was_drawn(self, panelled):
        assert E.panel_title(panelled, "p0") == "First half"
        assert any(e.text == "First half" and e.panel_id == "p0"
                   for e in panelled.elements)

    def test_a_panel_with_no_title_keeps_its_dimension_out_of_the_key(self, record):
        rows = E.build(record, key_scope="panel").grounded_table
        assert tuple(rows[0]["key"]) == ("Mercy General",)

    def test_the_scope_is_written_into_the_artifact(self, record, tmp_path):
        E.export([record], tmp_path, key_scope="panel")
        payload = json.loads((tmp_path / "f01_v0.json").read_text())
        assert payload["key_scope"] == "panel"

    def test_only_the_first_column_of_the_table_moves(self, panelled):
        narrow = E.build(panelled, key_scope="mark").grounded_table
        wide = E.build(panelled, key_scope="panel").grounded_table
        assert [r["values"] for r in narrow] == [r["values"] for r in wide]
        assert [r["box"] for r in narrow] == [r["box"] for r in wide]


class TestGranularity:
    def test_one_file_per_figure(self, record, tmp_path):
        written = E.export([record], tmp_path, granularity="figure")
        assert [p.name for p in written] == ["f01_v0.json"]

    def test_two_style_versions_of_one_figure_do_not_overwrite_each_other(
            self, record, tmp_path):
        """A figure is drawn more than once on purpose: the pair is a sample of its
        own and the input to the restyling check."""
        written = E.export([record, replace(record, variant=1)], tmp_path)
        assert {p.name for p in written} == {"f01_v0.json", "f01_v1.json"}

    def test_one_file_per_page(self, record, tmp_path):
        a = replace(record, figure_id="f01", page_id="pg01")
        b = replace(record, figure_id="f02", page_id="pg01")
        written = E.export([a, b], tmp_path, granularity="page")
        assert {p.name for p in written} == {"pg01.json"}

    def test_the_format_decides_what_is_written_and_the_granularity_what_goes_in_it(
            self, record, tmp_path):
        """Two settings, two questions: one page as a document and one page as a
        payload are the same records projected twice."""
        a = replace(record, figure_id="f01", page_id="pg01")
        b = replace(record, figure_id="f02", page_id="pg01")
        for form, expected in (("json", {"pg01.json"}), ("markdown", {"pg01.md"}),
                               ("both", {"pg01.json", "pg01.md"})):
            out = tmp_path / form
            written = E.export([a, b], out, granularity="page", format=form)
            assert {p.name for p in written} == expected, form


class TestThePageDocument:
    """What the markdown of one page looks like, and why. A benchmark that reads
    tables out of an answer searches every table in it and falls back to the text
    before a table when a label is nowhere inside it -- so the heading before each
    table is load-bearing, and so is one column per key segment."""

    def page(self, record, tmp_path, **kw):
        a = replace(record, figure_id="f01", page_id="pg01")
        b = replace(record, figure_id="f02", page_id="pg01")
        E.export([a, b], tmp_path, granularity="page", format="markdown", **kw)
        return (tmp_path / "pg01.md").read_text()

    def test_each_table_is_introduced_by_the_number_and_title_drawn_on_the_image(
            self, titled, tmp_path):
        text = self.page(titled, tmp_path)
        heading = E.figure_heading(titled)
        assert heading == "Figure 3. Wait times by hospital"
        assert f"## {heading}" in text

    def test_the_heading_is_never_the_file_identifier(self, titled, tmp_path):
        """`f01_v0` names a file and appears on the page nowhere, so a reader given
        the image could not have produced it."""
        assert "## f01_v0" not in self.page(titled, tmp_path)

    def test_a_figure_with_nothing_written_on_it_falls_back_to_its_identifier(
            self, record, tmp_path):
        bare = replace(record, page_id="pg01", elements=tuple(
            e for e in record.elements if e.category not in ("figure_number", "title")))
        E.export([bare], tmp_path, granularity="page", format="markdown")
        assert "## f01_v0" in (tmp_path / "pg01.md").read_text()

    def test_the_heading_carries_no_caption(self, titled, tmp_path):
        """A caption is a target of its own and says what cannot be read off the
        image. A document that folds it into the heading asks to be produced from
        something the reader was never shown."""
        text = self.page(titled, tmp_path)
        assert titled.caption
        assert titled.caption not in text

    def test_every_key_segment_gets_its_own_column(self, record, tmp_path):
        """A key folded into one cell reads as a single name; a mark addressed by a
        panel, a category and a colour group is three names."""
        width = max(len(m.key) for m in record.marks)
        text = self.page(record, tmp_path)
        header = next(line for line in text.split("\n") if line.startswith("| key 1"))
        assert header.count("key ") == width
        assert "| value |" in header

    def test_page_elements_are_merged_once_across_the_page(self, record, tmp_path):
        """Two figures on one page each know only their own text blocks, so exporting
        them apart leaves each target missing the other's."""
        a = replace(record, figure_id="f01", page_id="pg01")
        b = replace(record, figure_id="f02", page_id="pg01")
        E.export([a, b], tmp_path, granularity="page")
        payload = json.loads((tmp_path / "pg01.json").read_text())
        merged = payload["page_elements"]
        assert len(merged) == len({(tuple(e["box"]), e["category"], e["text"])
                                   for e in merged})
        assert len(merged) >= len(_furniture(a))

    def test_one_file_for_the_whole_batch(self, record, tmp_path):
        written = E.export([record, replace(record, figure_id="f02")], tmp_path,
                           granularity="batch")
        assert [p.name for p in written] == ["batch.json"]
        assert len(json.loads(written[0].read_text())["figures"]) == 2

    def test_a_query_is_written_in_what_the_page_says(self, record):
        """The axis title, not the column identifier: `wait_minutes` appears nowhere
        on the image, so a query written in it asks the reader to know the table."""
        axis = record.panels[0].axis(record.marks[0].value_axis)
        assert axis.label and axis.label != axis.column
        assert all(axis.label in row["query"] for row in E.build(record).mark_locate)

    def test_a_mark_measured_against_an_unnamed_axis_still_has_a_description(self, record):
        """A histogram's count axis names no column. Falling back to the axis object
        instead of to a word would put `None` in the query a model is asked."""
        from dataclasses import replace as swap

        from chartgen.interfaces.record import Axis

        blank = swap(record, panels=tuple(
            swap(p, axes=tuple(swap(a, column=None, label="") for a in p.axes))
            for p in record.panels))
        assert all(isinstance(a, Axis) for p in blank.panels for a in p.axes)
        assert all("None" not in row["query"] for row in E.build(blank).mark_locate)
        assert E.value_column(blank, blank.marks[0]) == "value"

    def test_figures_that_are_not_on_a_page_keep_their_own_elements(self, record):
        """Merging is by page, and a figure with no page is not on one. Merged
        anyway, every single-figure export would carry the page elements of every
        other figure exported beside it."""
        other = replace(record, figure_id="f02")
        units = E.with_whole_page([E.build(record), E.build(other)])
        assert all(u.page_id == "" for u in units)
        assert [len(u.page_elements) for u in units] == [len(_furniture(record))] * 2

    def test_a_target_left_out_is_simply_not_projected(self, record, tmp_path):
        E.export([record], tmp_path, targets=["grounded_table"])
        figure = json.loads((tmp_path / "f01_v0.json").read_text())["figures"][0]
        assert "grounded_table" in figure and "drilldown" not in figure


def _furniture(record) -> list:
    """The elements the page-element target speaks for.

    Tick labels are recorded with their own boxes but are not page furniture: in the
    vocabulary this target is written for, the whole chart is one Picture. Where a key
    was read from is the key-source target's question.
    """
    return [e for e in record.elements if e.category != "axis_tick"]


class TestSelfVerification:
    def test_a_correct_answer_passes_both_checks(self, record):
        got = V.verify(record.image_path, V.claims_of(record), record.panels)
        assert all(j.ok for j in got)
        assert V.consistency(got)["grounded"] == 1.0

    def test_an_invented_region_is_caught_with_no_ground_truth(self, record):
        claims = [replace(c, box=Box(600, 140, 700, 200)) for c in V.claims_of(record)]
        got = V.verify(record.image_path, claims, record.panels)
        assert not any(j.has_content for j in got)

    def test_a_value_that_does_not_match_its_region_is_caught(self, record):
        claims = [replace(c, values={k: v * 2 for k, v in c.values.items()})
                  for c in V.claims_of(record)]
        got = V.verify(record.image_path, claims, record.panels)
        assert not any(j.value_agrees for j in got)

    def test_a_verdict_needs_both_checks_to_hold(self, record):
        """`ok` is a conjunction. Read as either-or, a box with nothing in it passes
        as long as its number happens to be right, which is the case the geometric
        check exists for."""
        good = V.verify(record.image_path, V.claims_of(record), record.panels)
        assert all(j.ok for j in good)

        empty = [replace(c, box=Box(600, 140, 700, 200)) for c in V.claims_of(record)]
        assert not any(j.ok for j in
                       V.verify(record.image_path, empty, record.panels))

        wrong = [replace(c, values={k: v * 2 for k, v in c.values.items()})
                 for c in V.claims_of(record)]
        judged = V.verify(record.image_path, wrong, record.panels)
        assert all(j.has_content for j in judged) and not any(j.ok for j in judged)

    def test_a_claim_naming_no_panel_is_judged_against_the_first_one(self, record):
        """A model does not have to name a panel that exists. Judged against nothing
        the claim would raise; judged against the wrong panel it would be measured
        on another axis, so the fallback has to be the panel the figure starts with."""
        stray = [replace(c, panel_id="p9") for c in V.claims_of(record)]
        judged = V.verify(record.image_path, stray, record.panels)
        assert [j.measured for j in judged] == [
            j.measured for j in V.verify(record.image_path, V.claims_of(record),
                                         record.panels)]

    def test_a_claim_carries_every_number_the_mark_makes(self, record):
        """A mark's value is not always one number, and which numbers it holds is
        what decides the geometry it is measured on."""
        claims = V.claims_of(record)
        assert [c.values for c in claims] == [m.values for m in record.marks]

    def test_rounding_an_answer_cannot_widen_its_own_tolerance(self, record):
        """Inferred from the batch, the slack would depend on the other answers, and
        a model could buy itself room by rounding everything."""
        exact = V.claims_of(record)
        rounded = [replace(c, values={k: round(v) for k, v in c.values.items()})
                   for c in exact]
        alone = V.verify(record.image_path, rounded[:1], record.panels)
        together = V.verify(record.image_path, rounded, record.panels)
        assert [j.value_agrees for j in alone] == [j.value_agrees for j in together][:1]

    def test_the_reward_and_the_self_check_are_the_same_implementation(self):
        """Two copies of this arithmetic would eventually disagree, and silently."""
        import inspect

        from chartgen.common import readback
        from chartgen.s04_record import selfcheck

        assert readback.check_mark is not None
        assert "check_mark" in inspect.getsource(selfcheck)
        assert "check_mark" in inspect.getsource(V)

    def test_a_consistency_metric_needs_no_annotation_at_all(self, record):
        got = V.verify(record.image_path, V.claims_of(record), record.panels)
        stats = V.consistency(got)
        assert set(stats) == {"grounded", "consistent", "measured"}
        assert stats["consistent"] == 1.0


class TestExporterIsSelfSufficient:
    def test_it_reads_the_record_and_nothing_upstream(self):
        import ast
        from pathlib import Path

        source = Path("src/chartgen/s05_output/export.py").read_text()
        imported = {n.module or "" for n in ast.walk(ast.parse(source))
                    if isinstance(n, ast.ImportFrom)}
        stages = [m for m in imported if ".s0" in m or m.startswith("s0")]
        assert stages == [], stages


class TestTheRewardAgreesWithTheSelfCheck:
    """The same code, the same verdict. A perfect answer -- the record's own marks --
    has to come back perfect for every shape, or the reward is punishing the shapes
    whose value is not one number on one edge."""

    SHAPES = {
        "waterfall": ("checkout", dict(dims=("stage",), measures=("basket_value",),
                                       aggregate="SUM")),
        "stacked_bar": ("er", dict(dims=("hospital", "severity"), measures=("cost",),
                                   aggregate="SUM")),
        "box": ("er", dict(dims=("department",), measures=("wait_minutes",),
                           aggregate="FIVE_NUM")),
        "error_bar": ("er", dict(dims=("hospital",), measures=("wait_minutes",),
                                 aggregate="FIVE_NUM")),
        "area": ("er", dict(dims=("severity",), time="visit_date", measures=("cost",),
                            aggregate="SUM", resample="monthly")),
    }

    @pytest.mark.parametrize("name", sorted(SHAPES))
    def test_a_perfect_answer_scores_perfectly(self, tables, tmp_path, name):
        from chartgen.s02_figure.keys import key_sources
        from chartgen.s03_render.style import default

        scenario, binding_kw = self.SHAPES[name]
        table, schema = tables[scenario]
        binding = Binding(name, **binding_kw)
        binding = replace(binding, key_sources=key_sources(binding))
        view = project(table.df, binding, schema, seed=5)
        spec = FigureSpec(name, scenario, (PanelSpec("p0", (view,)),),
                          column_units={c.name: c.unit for c in schema.measures})
        record = finish(render(spec, default(), tmp_path / name), spec)

        got = V.verify(record.image_path, V.claims_of(record), record.panels,
                       V.quantum_of_record(record))
        wrong = [j.key for j in got if j.value_agrees is False]
        assert not wrong, (name, wrong[:3])
        assert V.consistency(got)["consistent"] == 1.0


class TestAPresetIsFourParametersAndNothingElse:
    """A benchmark asks for one shape of answer. What that changes is which projection
    is taken and how it is written out -- never what the record holds, which is what
    keeps one pipeline able to serve more than one benchmark without being shaped by
    any of them."""

    def resolve(self, preset=None, **overrides):
        return E.settings(lambda key: overrides.get(key), preset)

    def test_with_no_preset_the_defaults_stand(self):
        chosen = self.resolve()
        assert chosen == {"key_scope": "mark", "granularity": "figure",
                          "format": "json", "targets": E.TARGETS}

    def test_the_parsebench_preset_asks_for_a_page_of_markdown(self):
        """One page is one image and one answer; every table in the answer is searched;
        a spot check may need three keys to be addressed."""
        chosen = self.resolve("parsebench")
        assert chosen["granularity"] == "page"
        assert chosen["format"] == "markdown"
        assert chosen["key_scope"] == "full"
        assert chosen["targets"] == ("grounded_table",)

    def test_anything_set_beside_a_preset_wins(self):
        chosen = self.resolve("parsebench", format="both")
        assert chosen["format"] == "both"
        assert chosen["granularity"] == "page", "the rest of the preset still stands"

    def test_an_unknown_preset_leaves_the_defaults(self):
        assert self.resolve("nothing-by-this-name")["granularity"] == "figure"

    def test_the_preset_produces_one_markdown_per_page(self, titled, tmp_path):
        a = replace(titled, figure_id="f01", page_id="pg01")
        b = replace(titled, figure_id="f02", page_id="pg01")
        chosen = self.resolve("parsebench")
        written = E.export([a, b], tmp_path, key_scope=chosen["key_scope"],
                           granularity=chosen["granularity"], targets=chosen["targets"],
                           format=chosen["format"])
        assert [p.name for p in written] == ["pg01.md"]
        text = written[0].read_text()
        assert text.count("## Figure 3.") == 2, "one heading per figure on the page"
