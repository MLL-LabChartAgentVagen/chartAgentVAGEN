"""Choosing which figures a scenario yields: built, derived, sampled, then named."""

import numpy as np
import pytest

from chartgen.config import Config
from chartgen.interfaces.figure import Binding
from chartgen.s02_figure import sampling, title
from chartgen.s02_figure.compose import compose, compose_with_log, draw_binding
from chartgen.s02_figure.keys import key_sources


@pytest.fixture(scope="module")
def config():
    return Config.load()


@pytest.fixture(scope="module")
def batch(er_table, er_schema, config):
    return compose_with_log(er_table, er_schema, 20260816, config)


class TestThreeWaysIn:
    def test_one_figure_per_intent_where_the_family_allows_one(self, batch, er_schema):
        figures, log = batch
        built = [f for f in figures if f.source.kind == "intent"]
        assert [f.source.intent_index for f in built] == list(range(len(er_schema.intents)))

    def test_the_first_intent_becomes_a_bar_over_the_column_it_named(self, batch):
        first = next(f for f in batch[0] if f.source.intent_index == 0)
        assert first.chart_types == ("bar",)
        assert first.panels[0].view.binding.dims == ("hospital",)
        assert [d.key[0] for d in first.panels[0].view.data] == [
            "Mercy General", "St. Luke's", "Riverside"]

    def test_the_trend_intent_is_resampled_until_the_points_are_readable(self, batch):
        second = next(f for f in batch[0] if f.source.intent_index == 1)
        assert second.panels[0].view.binding.resample == "monthly"
        assert len(second.panels[0].view.data) == 6

    def test_every_derived_figure_names_the_anchor_it_came_from(self, batch):
        figures = batch[0]
        ids = {f.figure_id for f in figures}
        for f in figures:
            if f.source.kind in ("panel", "overlay"):
                assert f.source.anchor_figure_id in ids

    def test_an_anchor_is_always_a_figure_that_stands_on_its_own(self, batch):
        """A view derived from something that appears nowhere else takes the layout
        pairing with it: the same keys drawn twice at different pixels is the point."""
        figures = batch[0]
        alone = {f.figure_id for f in figures if len(f.panels) == 1}
        for f in figures:
            if f.source.anchor_figure_id:
                assert f.source.anchor_figure_id in alone

    def test_the_rotation_adds_types_the_other_two_paths_did_not(self, batch):
        figures, _ = batch
        built = {t for f in figures if f.source.kind == "intent" for t in f.chart_types}
        sampled = {t for f in figures if f.source.kind == "rotation" for t in f.chart_types}
        assert sampled - built


class TestBudgetAndDiversity:
    def test_the_budget_is_an_upper_bound_not_a_target(self, batch, config):
        assert len(batch[0]) <= int(config.get("figure.k_max"))

    def test_no_two_standalone_figures_share_keys_and_a_mark_shape(self, batch):
        from chartgen.s02_figure.admit import figure_signature

        seen = set()
        for f in batch[0]:
            if f.source.kind == "rotation" or f.source.kind == "intent":
                if len(f.panels) == 1 and not f.page_id:
                    sig = figure_signature(f)
                    assert sig not in seen, f.figure_id
                    seen.add(sig)

    def test_the_run_says_why_candidates_were_turned_away(self, batch):
        assert batch[1]["rejected"]
        assert batch[1]["skipped"]

    def test_how_many_figures_came_out_is_reported_by_path(self, batch):
        counts = batch[1]["counts"]
        assert counts["total"] == sum(v for k, v in counts.items() if k != "total")


class TestPageComposition:
    """A relation puts a second view somewhere. Two of the three somewheres are the
    same plotting area and another plotting area on the same image; a page is the
    third. Which relation a scenario spends its page on moves with the scenario id,
    so these say what every page has to be true of rather than naming one relation."""

    def test_a_page_holds_at_least_two_figures_and_no_figure_sits_on_two(self, batch):
        pages = [f for f in batch[0] if f.page_id]
        assert pages
        for page in {f.page_id for f in pages}:
            assert len([f for f in pages if f.page_id == page]) >= 2

    def test_no_page_carries_a_relation_drawn_in_one_plotting_area(self, batch):
        """Two overlaid views say these numbers are read against each other, and a
        page separates them."""
        from chartgen.s02_figure.panel import OVERLAY_RELATIONS

        overlaid = {r.__name__ for r in OVERLAY_RELATIONS}
        assert not [f for f in batch[0] if f.page_id and f.relation in overlaid]

    def test_the_members_of_a_page_can_be_told_apart(self, batch):
        """Either their keys already differ, or a segment read off each figure's own
        heading says which is which. Split into separate images, identical keys with
        nothing to join them by is one key with two answers."""
        pages = [f for f in batch[0] if f.page_id]
        for page in {f.page_id for f in pages}:
            members = [f for f in pages if f.page_id == page]
            keys = [f.panels[0].view.keys for f in members]
            shared = any(a & b for i, a in enumerate(keys) for b in keys[i + 1:])
            if not shared:
                continue
            for member in members:
                view = member.panels[0].view
                assert view.key_prefix and view.prefix_source == ("heading",)
                assert view.key_src(view.data[0])[0] == "heading"
            assert len({f.panels[0].view.key_prefix for f in members}) == len(members)

    def test_a_page_of_one_relation_is_never_half_made(self, batch):
        """Half a page is a figure whose partner says what it is."""
        pages = [f for f in batch[0] if f.page_id]
        for page in {f.page_id for f in pages}:
            members = [f for f in pages if f.page_id == page]
            assert len({f.relation for f in members}) == 1


class TestKeySources:
    def test_a_single_grouping_column_is_read_off_the_axis(self):
        assert key_sources(Binding("bar", dims=("hospital",))) == ("axis_tick",)

    def test_the_inner_grouping_column_is_read_off_the_legend(self):
        assert key_sources(Binding("grouped_bar", dims=("hospital", "department"))) == (
            "axis_tick", "legend")

    def test_a_sector_is_labelled_beside_itself(self):
        assert key_sources(Binding("pie", dims=("department",))) == ("inline_label",)

    def test_a_row_identifier_is_written_nowhere(self):
        assert key_sources(Binding("scatter", measures=("a", "b"))) == ("not_shown",)
        assert key_sources(Binding("scatter", dims=("severity",), measures=("a", "b"))) == (
            "legend", "not_shown")

    def test_a_colour_group_adds_a_segment_carried_by_colour_alone(self):
        binding = Binding("bar", dims=("site",), colour_group="region",
                          key_sources=("axis_tick", "colour_only"))
        assert key_sources(binding)[-1] == "colour_only"

    def test_the_parent_of_the_innermost_grouping_becomes_a_colour_group(self, logistics):
        """A site reports to one region, so the region is a second name the mark
        already has and colour can carry it. It is read off the innermost grouping
        column: the outer ones are already on an axis or in a legend."""
        from chartgen.s02_figure.keys import with_colour_group

        table, schema = logistics
        binding = Binding("bar", dims=("site",), measures=("parcels",), aggregate="SUM")
        with_group = with_colour_group(binding, table.df, schema)
        assert with_group.colour_group == "region"
        assert with_group.key_sources[-1] == "colour_only"

    def test_it_is_the_innermost_grouping_column_that_is_looked_at(self, logistics):
        """The outer columns are already on an axis. Reading the parent off the first
        one instead would put a region into the key of a figure grouped by shift."""
        from chartgen.s02_figure.keys import with_colour_group

        table, schema = logistics
        inner = Binding("grouped_bar", dims=("shift", "site"), measures=("parcels",),
                        aggregate="SUM")
        assert with_colour_group(inner, table.df, schema).colour_group == "region"
        outer = Binding("grouped_bar", dims=("site", "shift"), measures=("parcels",),
                        aggregate="SUM")
        assert with_colour_group(outer, table.df, schema).colour_group is None

    def test_a_grouping_that_already_holds_the_parent_gains_nothing(self, logistics):
        from chartgen.s02_figure.keys import with_colour_group

        table, schema = logistics
        already = Binding("grouped_bar", dims=("region", "site"),
                          measures=("parcels",), aggregate="SUM")
        assert with_colour_group(already, table.df, schema).colour_group is None
        parentless = Binding("bar", dims=("shift",), measures=("parcels",),
                             aggregate="SUM")
        assert with_colour_group(parentless, table.df, schema).colour_group is None

    def test_the_batch_produces_four_different_sources(self, batch):
        got = {s for f in batch[0] for v in f.views for d in v.data for s in v.key_src(d)}
        assert {"axis_tick", "legend", "inline_label", "not_shown"} <= got

    def test_a_page_whose_members_share_their_keys_reads_one_off_the_heading(
            self, er_table, er_schema, config):
        """The fifth source. A time comparison puts the same categories under two
        windows, and split into two images only what is written on each says which
        half it is."""
        from chartgen.s02_figure import compose as C
        from chartgen.s02_figure.admit import Batch
        from chartgen.s02_figure.panel import Context, time_split

        ctx = Context(er_table.df, er_schema, seed=11)
        anchors, _ = C.intent_figures(ctx, Batch(), er_schema)
        made, _ = C.page_figures(anchors, ctx, Batch(), er_schema, 20,
                                 rules=(time_split,), budget=1)
        assert len(made) == 2
        for spec in made:
            view = spec.panels[0].view
            assert view.prefix_source == ("heading",)
            assert view.key_src(view.data[0])[0] == "heading"


class TestWhatTheLogCounts:
    def test_a_shared_legend_needs_both_the_flag_and_a_series_column(self):
        """`share_legend` without a series column is a legend covering panels that
        group by different things, which is the one thing a shared legend may not be.
        Counted as shared, it would overstate how many figures the legend-binding
        target can come from."""
        from chartgen.interfaces.figure import (
            FigureSpec, PanelSpec, Sharing, ViewSpec)
        from chartgen.s02_figure.compose import _layout_counts

        def figure(**sharing):
            view = ViewSpec(Binding("bar", dims=("hospital",), measures=("wait",),
                                    aggregate="AVG"), ())
            return FigureSpec("f", "s", (PanelSpec("p0", (view,)),
                                         PanelSpec("p1", (view,))),
                              sharing=Sharing(**sharing))

        both = figure(share_legend=True, series_column="severity")
        flag_only = figure(share_legend=True)
        column_only = figure(series_column="severity")
        counts = _layout_counts([both, flag_only, column_only])
        assert counts["multi_panel"] == 3 and counts["shared_legend"] == 1


class TestSampling:
    def test_the_uniform_preset_is_the_fixed_walk_itself(self):
        rng = np.random.default_rng(0)
        order = sampling.rotation_order(sampling.slots(), ["comparison"], rng,
                                        sampling.PRESETS["uniform"])
        assert order[0] == "trend" and order[-1] == "comparison"

    def test_weights_that_add_up_to_nothing_still_return_every_slot(self):
        """Weights order the rotation, they do not veto a family. All-zero weights
        are still an order -- and dropping through the draw has to keep every slot,
        or a preset could empty the batch."""
        rng = np.random.default_rng(1)
        zero = sampling.Weights("zero", {name: 0.0 for name in sampling.FAMILIES})
        order = sampling.rotation_order(sampling.slots(), [], rng, zero)
        assert sorted(map(str, order)) == sorted(map(str, sampling.slots()))

    def test_a_type_that_answers_no_view_class_is_only_reachable_in_its_tier(self):
        """The slot appears at the tier the type sits in, not one past it: a table
        chart is second tier, so a run capped at the second tier still reaches it."""
        from chartgen.registry.charts import familyless

        tier = min(c.tier for c in familyless())
        assert None in sampling.slots(max_tier=tier)
        assert None not in sampling.slots(max_tier=tier - 1)

    def test_a_weights_file_that_is_not_there_says_so(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="preset"):
            sampling.load(str(tmp_path / "nowhere.json"))
        assert sampling.load(None) is sampling.PRESETS["uniform"]

    def test_a_preset_orders_the_gaps_before_anything_already_drawn(self):
        rng = np.random.default_rng(3)
        order = sampling.rotation_order(sampling.slots(), ["comparison"], rng,
                                        sampling.PRESETS["parsebench"])
        assert order[-1] == "comparison"

    def test_weights_are_keyed_by_name_so_a_new_type_cannot_shift_them(self):
        assert set(sampling.PARSEBENCH_WEIGHTS) <= set(
            [*sampling.PRESETS["parsebench"].by_name] + [sampling.FAMILYLESS])

    def test_the_preset_lands_beside_the_batch(self, batch):
        assert batch[1]["family_weights"]["preset"] == "uniform"

    def test_an_unknown_preset_is_an_error_rather_than_a_silent_default(self):
        with pytest.raises(FileNotFoundError):
            sampling.load("whatever")

    def test_changing_the_preset_changes_which_figures_come_out(self, er_table, er_schema):
        under = Config.load().set("figure.family_weights", "parsebench")
        other, _ = compose_with_log(er_table, er_schema, 20260816, under)
        base, _ = compose_with_log(er_table, er_schema, 20260816, Config.load())
        sampled = lambda fs: [f.chart_types for f in fs if f.source.kind == "rotation"]
        assert sampled(other) != sampled(base) or len(other) != len(base)

    def test_a_drawn_binding_is_always_legal(self, er_schema):
        from chartgen.registry.charts import DEFAULT_BAND
        from chartgen.registry.conditions import check

        rng = np.random.default_rng(5)
        drawn = [draw_binding("comparison", er_schema, rng, max_tier=3, density=DEFAULT_BAND)
                 for _ in range(40)]
        legal = [b for b in drawn if b is not None]
        assert legal and all(check(b, er_schema) for b in legal)


class TestDeterminism:
    def test_the_same_seed_gives_the_same_batch(self, er_table, er_schema, config):
        a = compose(er_table, er_schema, 20260816, config)
        b = compose(er_table, er_schema, 20260816, config)
        assert a == b

    def test_another_seed_moves_only_the_sampled_figures(self, er_table, er_schema, config):
        a = compose(er_table, er_schema, 20260816, config)
        b = compose(er_table, er_schema, 999, config)
        keep = lambda fs: [f.chart_types for f in fs if f.source.kind != "rotation"]
        assert keep(a) == keep(b)


def unwritten(specs):
    """The batch as view selection hands it over: chosen, but with no text yet.

    A block that is already there is kept, so writing over a batch that has been
    written once says nothing about what the writer produced."""
    from dataclasses import replace as swap

    return [swap(s, texts=()) for s in specs]


#: Distinct words to tell one made-up title from another. Figure ids are unusable
#: here: a digit in a title is refused, and every figure id has one.
LETTER = [chr(ord("a") + i) for i in range(26)]


class TestTitles:
    def test_every_figure_is_given_a_title(self, batch):
        assert all(f.text("title") for f in batch[0])

    def test_every_column_gets_a_readable_name(self, batch, er_schema):
        used = {c for f in batch[0] for v in f.views
                for c in (*v.binding.group_columns, *v.binding.measures)}
        for f in batch[0]:
            assert used <= set(f.column_names)

    def test_a_title_that_states_a_finding_is_rejected(self, batch):
        specs = batch[0]
        payload = {"figures": [{"figure_id": s.figure_id, "title": "Wait times fell by 12",
                                "subtitle": "", "unit": "minutes"} for s in specs],
                   "column_names": {"wait_minutes": "Wait"}}
        with pytest.raises(title.TitleRejected):
            title.validate(payload, specs)

    def test_a_year_or_a_quarter_is_allowed(self):
        assert title.numbers_in("Average per visit, Jan-Jun 2024, Q1") == []
        assert title.numbers_in("Wait times fell 12 percent") == ["12"]

    def test_a_missing_figure_is_rejected(self, batch):
        specs = batch[0]
        payload = {"figures": [{"figure_id": specs[0].figure_id, "title": "A", "subtitle": "",
                                "unit": ""}], "column_names": {"a": "A"}}
        with pytest.raises(title.TitleRejected):
            title.validate(payload, specs)

    def test_a_model_answer_is_what_gets_drawn(self, batch, er_schema):
        """The suite runs with no model, so the template path is the one it usually
        walks. This is the other one: an answer arrives, is accepted, and its words
        are what the figures carry."""
        specs = unwritten(batch[0])

        # No digits anywhere: a title that states a number is refused, and a figure
        # identifier has one in it.
        class Answering:
            def json(self, system, prompt, schema=None):
                # Distinct per figure: two figures under one title is one name for
                # two different pictures, and the check refuses it.
                return {"figures": [{"figure_id": s.figure_id,
                                     "title": f"Written by the model, part {LETTER[i]}",
                                     "subtitle": "By the model", "unit": "minutes"}
                                    for i, s in enumerate(specs)],
                        "column_names": {c: c.replace("_", " ").title()
                                         for c in title.columns_of(specs)}}

        log: list[str] = []
        written = title.write(specs, er_schema, llm=Answering(), report=log)
        assert all(f.text("title").startswith("Written by the model") for f in written)
        assert all(f.text("subtitle") == "By the model" for f in written)
        assert "written by the model" in " ".join(log)

    def test_an_answer_that_is_rejected_twice_falls_back_to_the_templates(self, batch,
                                                                          er_schema):
        specs = unwritten(batch[0])

        class Refusing:
            def __init__(self):
                self.calls = 0

            def json(self, system, prompt, schema=None):
                self.calls += 1
                return {"figures": [{"figure_id": s.figure_id, "title": "Wait fell by 12",
                                     "subtitle": "", "unit": ""} for s in specs],
                        "column_names": {c: c for c in title.columns_of(specs)}}

        model = Refusing()
        log: list[str] = []
        written = title.write(specs, er_schema, llm=model, retries=2, report=log)
        assert model.calls == 3, "it is asked again with the reason it was refused"
        assert all(f.text("title") and "12" not in f.text("title") for f in written)
        assert "written from the templates" in " ".join(log)

    def test_a_call_that_raises_is_not_a_failed_run(self, batch, er_schema):
        specs = unwritten(batch[0])

        class Broken:
            def json(self, system, prompt, schema=None):
                raise RuntimeError("no key")

        log: list[str] = []
        written = title.write(specs, er_schema, llm=Broken(), report=log)
        assert all(f.text("title") for f in written)
        assert "the call failed" in " ".join(log)

    def test_column_names_have_to_be_a_mapping(self, batch):
        specs = batch[0]
        payload = {"figures": [{"figure_id": s.figure_id, "title": f"A {LETTER[i]}",
                                "subtitle": "", "unit": ""} for i, s in enumerate(specs)],
                   "column_names": [["wait_minutes", "Wait"]]}
        with pytest.raises(title.TitleRejected, match="mapping"):
            title.validate(payload, specs)

    def test_two_figures_may_not_be_given_the_same_title(self, batch):
        """The batch is written in one call so that this can be checked: the model
        sees all sixteen at once, and a title that does not tell its figure from
        another one has not named anything."""
        specs = batch[0]
        payload = {"figures": [{"figure_id": s.figure_id, "title": "Wait by hospital",
                                "subtitle": "per centre", "unit": ""} for s in specs],
                   "column_names": {c: c for c in title.columns_of(specs)}}
        with pytest.raises(title.TitleRejected, match="same title"):
            title.validate(payload, specs)

    def test_the_same_title_under_two_subtitles_is_allowed(self, batch):
        """A subtitle is the documented way two figures over one quantity are told
        apart, so the rule is on the pair rather than on the title alone."""
        specs = batch[0]
        payload = {"figures": [{"figure_id": s.figure_id, "title": "Wait by hospital",
                                "subtitle": f"part {LETTER[i]}", "unit": ""}
                               for i, s in enumerate(specs)],
                   "column_names": {c: c for c in title.columns_of(specs)}}
        assert title.validate(payload, specs) is payload

    def test_the_request_carries_no_data_value(self, batch, er_schema):
        """The writer names what is drawn. Handing it the numbers would let a title
        state one, and a title is painted on the image and read as truth there."""
        text = title.request(batch[0], er_schema)
        for f in batch[0]:
            for v in f.views:
                for d in v.data:
                    for number in d.values.values():
                        if abs(number) >= 10:
                            assert f"{number:.1f}" not in text
