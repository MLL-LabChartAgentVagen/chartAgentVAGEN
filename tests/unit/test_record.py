"""Joining the layers, deciding what can be read, and the three self-checks."""

from dataclasses import replace

import pytest

from chartgen.common import readback as rb
from chartgen.common.geometry import Box
from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
from chartgen.s02_figure.project import project
from chartgen.s03_render.render import render
from chartgen.s03_render.style import default
from chartgen.s04_record import merge, readable, selfcheck

UNITS = {"wait_minutes": "minutes", "cost": "USD", "satisfaction": "points"}


def spec_for(er_table, er_schema, chart_type="bar", **binding_kw):
    binding = Binding(chart_type, key_sources=("axis_tick",), **binding_kw)
    view = project(er_table.df, binding, er_schema, seed=3)
    return FigureSpec("f01", "er", (PanelSpec("p0", (view,)),), column_units=UNITS)


@pytest.fixture(scope="module")
def bar(er_table, er_schema, tmp_path_factory):
    spec = spec_for(er_table, er_schema, dims=("hospital",),
                    measures=("wait_minutes",), aggregate="AVG")
    out = render(spec, default(), tmp_path_factory.mktemp("rec"))
    return spec, out


class TestMerge:
    def test_every_mark_gets_the_row_count_behind_it(self, bar):
        spec, out = bar
        record = merge.merge(out, spec)
        assert all(m.rows is not None for m in record.marks)
        assert sum(m.rows for m in record.marks) == 900

    def test_the_join_is_a_lookup_and_notices_when_it_misses(self, bar):
        spec, out = bar
        moved = replace(out, marks=tuple(
            replace(m, key=("nobody",)) for m in out.marks))
        assert len(merge.unmatched(merge.merge(moved, spec))) == len(out.marks)

    def test_the_provenance_layer_can_be_switched_off_on_its_own(self, bar):
        spec, out = bar
        record = merge.merge(out, spec, provenance=False)
        assert all(m.rows is None for m in record.marks)
        assert len(record.marks) == len(out.marks)

    def test_the_other_two_layers_survive_the_join(self, bar):
        spec, out = bar
        record = merge.merge(out, spec)
        assert record.elements and record.panels
        assert record.image_path == out.image_path


class TestReadable:
    def test_a_measurable_bar_on_its_own_axis_is_readable(self, bar):
        spec, out = bar
        record = readable.apply(merge.merge(out, spec))
        assert all(m.readable for m in record.marks)

    def test_the_same_bar_on_an_axis_a_hundred_times_larger_is_not(self, bar):
        spec, out = bar
        panel = out.panels[0]
        stretched = replace(out, panels=(replace(panel, axes=tuple(
            replace(a, value_range=(0.0, 6000.0)) if a.role == "y" else a
            for a in panel.axes)),))
        record = readable.apply(merge.merge(stretched, spec))
        assert not any(m.readable for m in record.marks)
        assert readable.rate(record) == 0.0

    def test_a_key_no_part_of_the_page_names_loses_its_value_target(
            self, er_table, er_schema, tmp_path):
        """A scatter point is addressed by a row identifier that is written nowhere,
        so there is no question whose answer is its value. It keeps its box."""
        binding = Binding("scatter", measures=("wait_minutes", "satisfaction"),
                          aggregate="NONE", key_sources=("not_shown",))
        view = project(er_table.df, binding, er_schema, seed=3)
        spec = FigureSpec("f02", "er", (PanelSpec("p0", (view,)),), column_units=UNITS)
        from chartgen.interfaces.record import Mark, Panel, RenderOutput
        marks = tuple(Mark(f"m{i}", "p0", view.full_key(d), dict(d.values),
                           Box(100 + i, 100, 108 + i, 108), "position",
                           mark_shape="point", key_src=view.key_src(d))
                      for i, d in enumerate(view.data[:5]))
        out = RenderOutput("f02", "er", "none.png", (900, 600), default(),
                           panels=(Panel("p0", Box(96, 132, 860, 480),
                                         (rb.Axis("y", (0.0, 5.0), (480.0, 132.0)),),
                                         ("scatter",)),),
                           marks=marks)
        record = readable.apply(merge.merge(out, spec))
        assert not any(m.readable for m in record.marks)
        assert all(m.box is not None for m in record.marks)

    def test_a_written_value_is_readable_whatever_the_geometry(self, bar):
        spec, out = bar
        labelled = replace(out, marks=tuple(replace(m, labeled=True) for m in out.marks))
        panel = labelled.panels[0]
        stretched = replace(labelled, panels=(replace(panel, axes=tuple(
            replace(a, value_range=(0.0, 6000.0)) if a.role == "y" else a
            for a in panel.axes)),))
        record = readable.apply(merge.merge(stretched, spec))
        assert all(m.readable for m in record.marks)

    def test_the_tolerance_the_caller_passes_is_the_one_that_decides(self, bar):
        spec, out = bar
        panel = out.panels[0]
        stretched = replace(out, panels=(replace(panel, axes=tuple(
            replace(a, value_range=(0.0, 300.0)) if a.role == "y" else a
            for a in panel.axes)),))
        joined = merge.merge(stretched, spec)
        assert not any(m.readable for m in readable.apply(joined).marks)
        assert all(m.readable for m in readable.apply(joined, tolerance=0.1).marks)


class TestAWedgeIsAskedAboutItsShare:
    """A wedge holds two numbers and only one of them is on the page. The angle gives
    the share; turning that into the value would need the total, and a pie writes the
    total nowhere. So which number a value target asks about is settled here, beside
    whether it can be read at all -- the two are one decision, and a wedge asked about
    its value would be readable and wrong at the same time."""

    def pie(self, er_table, er_schema, tmp_path, **style):
        from dataclasses import replace as _replace

        from chartgen.s03_render.render import render

        view = project(er_table.df, Binding("pie", dims=("hospital",),
                                            measures=("wait_minutes",), aggregate="SUM",
                                            key_sources=("inline_label",)), er_schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),), column_units=UNITS)
        return spec, render(spec, _replace(default(), **style), tmp_path / "pie")

    def test_an_unlabelled_wedge_is_asked_about_its_share(self, er_table, er_schema,
                                                          tmp_path):
        spec, out = self.pie(er_table, er_schema, tmp_path)
        record = readable.apply(merge.merge(out, spec))
        assert all(m.value_key == "share" for m in record.marks)

    def test_a_wedge_with_its_value_written_on_it_is_asked_about_the_value(
            self, er_table, er_schema, tmp_path):
        spec, out = self.pie(er_table, er_schema, tmp_path, value_labels="all")
        record = readable.apply(merge.merge(out, spec))
        assert all(m.value_key == "value" for m in record.marks)
        assert all(m.readable for m in record.marks)

    def test_a_bar_is_still_asked_about_its_value(self, bar):
        spec, out = bar
        record = readable.apply(merge.merge(out, spec))
        assert all(m.value_key == "value" for m in record.marks)

    def test_a_wedge_reads_at_five_percent_and_not_at_one(self, er_table, er_schema,
                                                          tmp_path):
        """The grading in one test: the same three wedges, two tolerances, two
        answers. A single verdict could give only one of them."""
        spec, out = self.pie(er_table, er_schema, tmp_path)
        joined = merge.merge(out, spec)
        assert not any(m.readable for m in readable.apply(joined).marks)
        assert all(m.readable for m in readable.apply(joined, tolerance=0.05).marks)

    def test_the_exported_value_of_a_wedge_is_its_share(self, er_table, er_schema,
                                                        tmp_path):
        from chartgen.s05_output import export

        spec, out = self.pie(er_table, er_schema, tmp_path)
        record = readable.apply(merge.merge(out, spec), tolerance=0.05)
        built = export.build(record)
        for row in built.mark_read:
            assert 0.0 < row["value"] < 1.0, "a value target on a pie asks for a share"


class TestSelfChecks:
    def test_a_correct_figure_passes_the_first_two(self, bar):
        spec, out = bar
        record = selfcheck.finish(out, spec)
        assert record.selfcheck.box_content and record.selfcheck.value_readback
        assert record.selfcheck.passed

    def test_shifting_every_box_off_its_mark_is_caught(self, bar):
        spec, out = bar
        shifted = replace(out, marks=tuple(
            replace(m, box=Box(m.box.x0 + 130, m.box.y0, m.box.x1 + 130, m.box.y1))
            for m in out.marks))
        record = selfcheck.run(selfcheck.finish(shifted, spec))
        assert not record.selfcheck.box_content
        assert record.selfcheck.reasons

    def test_a_mis_mapped_axis_is_caught_by_the_second_check_alone(self, bar):
        spec, out = bar
        panel = out.panels[0]
        broken = replace(out, panels=(replace(panel, axes=tuple(
            replace(a, value_range=(0.0, 15.0)) if a.role == "y" else a
            for a in panel.axes)),))
        record = selfcheck.finish(broken, spec)
        assert record.selfcheck.box_content
        assert not record.selfcheck.value_readback

    def test_the_checks_read_the_background_off_the_panel_not_off_white(
            self, er_table, er_schema, tmp_path):
        """With a tinted panel, judging ink against white makes every box look full
        and turns the first check into one that can never fail."""
        spec = spec_for(er_table, er_schema, dims=("hospital",),
                        measures=("wait_minutes",), aggregate="AVG")
        tinted = render(spec, replace(default(), panel_bg="tint"), tmp_path)
        shifted = replace(tinted, marks=tuple(
            replace(m, box=Box(m.box.x0 + 130, m.box.y0, m.box.x1 + 130, m.box.y1))
            for m in tinted.marks))
        assert not selfcheck.finish(shifted, spec).selfcheck.box_content

    def test_two_style_versions_have_to_agree_key_by_key(self, er_table, er_schema, tmp_path):
        spec = spec_for(er_table, er_schema, dims=("hospital",),
                        measures=("wait_minutes",), aggregate="AVG")
        first = selfcheck.finish(render(spec, default(), tmp_path / "a"), spec)
        second = selfcheck.finish(
            render(spec, replace(default(), palette="grayscale", value_labels="all"),
                   tmp_path / "b"), spec)
        assert selfcheck.style_invariant(first, second)[0]
        checked = selfcheck.run(first, variant=second)
        assert checked.selfcheck.style_invariant

    def test_a_style_that_moved_a_value_would_be_caught(self, bar):
        spec, out = bar
        record = selfcheck.finish(out, spec)
        tampered = replace(record, marks=tuple(
            replace(m, values={"value": m.values["value"] + 1}) for m in record.marks))
        ok, why = selfcheck.style_invariant(record, tampered)
        assert not ok and "changed the answers" in why

    def test_the_third_check_is_not_run_when_there_is_nothing_to_compare(self, bar):
        spec, out = bar
        assert selfcheck.finish(out, spec).selfcheck.style_invariant is None

    def test_a_rounded_column_gets_at_least_half_a_step_of_slack(self):
        """One percent of a satisfaction score near four is smaller than the rounding
        the column was recorded with, so the percentage alone would fail on arithmetic."""
        assert selfcheck.quantum_of([4.0, 3.7, 4.2, 3.1]) == pytest.approx(0.1)
        assert selfcheck.quantum_of([42.317, 35.81]) == 0.0
        assert selfcheck.quantum_of([980.0, 610.0]) == pytest.approx(1.0)

    def test_a_value_read_between_two_edges_is_allowed_twice_the_slack(self):
        """A stacked segment's value is a difference of two readings, so two
        readings' worth of rounding goes into it. The rule is checked where the check
        applies it, not in a helper nothing calls."""
        import numpy as np

        from chartgen.common import readback as rb
        from chartgen.interfaces.record import Axis, Mark, Panel

        axis = Axis("y", (0.0, 60.0), (480.0, 132.0))
        panel = Panel("p0", Box(96, 132, 860, 480), (axis,), ("stacked_bar",))
        img = np.full((600, 900, 3), 255, np.uint8)
        img[200:400, 200:300] = (31, 78, 121)
        box = Box(200, 200, 300, 400)
        top = rb.value_from_box(box, rb.axis_pair(axis), "top")
        bottom = rb.value_from_box(box, rb.axis_pair(axis), "bottom")
        drift = 3.0 * (60 / 348)
        stacked = Mark("m1", "p0", ("a",), {"value": top - bottom,
                                            "cum_start": bottom + drift,
                                            "cum_end": top + drift}, box, "length")
        plain = Mark("m0", "p0", ("a",), {"value": top + drift}, box, "length")
        assert rb.check_mark(img, stacked, panel).value_agrees
        assert not rb.check_mark(img, plain, panel).value_agrees
