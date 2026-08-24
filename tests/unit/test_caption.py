"""What a figure is for, in a sentence.

The caption is the one training target whose content cannot be read off the image,
which is the whole reason it is worth having -- and the reason it needs a test of its
own: a caption that only repeats the axis names would pass every other check in the
pipeline while teaching nothing.
"""

import pytest

from chartgen.interfaces.figure import Binding, Datum, FigureSpec, PanelSpec, Source, ViewSpec
from chartgen.s02_figure import caption as C


def figure(binding, **kw):
    view = ViewSpec(binding, (Datum(("Mercy General",), {"value": 42.3}, 372),))
    return FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                      column_names={"wait_minutes": "Average wait", "hospital": "Hospital",
                                    "cost": "Cost per visit"}, **kw)


BAR = Binding("bar", dims=("hospital",), measures=("wait_minutes",), aggregate="AVG")


class TestWhatAFigureShows:
    def test_it_names_the_measure_and_how_it_is_broken_down(self, er_schema):
        got = C.describe(figure(BAR), er_schema)
        assert got == "Average wait by Hospital."

    def test_an_aggregate_already_in_the_name_is_not_said_twice(self, er_schema):
        """The readable names come from a model, and a model asked to name a column
        of averages writes `Average wait`. Prefixing the aggregate again gives
        "Average Average wait", on the axis title as much as in the caption."""
        assert "Average Average" not in C.describe(figure(BAR), er_schema)
        summed = Binding("bar", dims=("hospital",), measures=("cost",), aggregate="SUM")
        assert C.describe(figure(summed), er_schema) == "Total Cost per visit by Hospital."

    def test_it_uses_the_prose_names_rather_than_the_column_names(self, er_schema):
        assert "wait_minutes" not in C.describe(figure(BAR), er_schema)

    def test_an_aggregate_reads_as_a_word(self, er_schema):
        summed = Binding("bar", dims=("hospital",), measures=("cost",), aggregate="SUM")
        assert C.describe(figure(summed), er_schema).startswith("Total ")

    def test_a_projection_shape_reads_as_a_phrase_about_the_column(self, er_schema):
        spread = Binding("box", dims=("hospital",), measures=("wait_minutes",),
                         aggregate="FIVE_NUM")
        assert "the spread of" in C.describe(figure(spread), er_schema).lower()

    def test_a_figure_that_answers_no_intent_is_described_by_its_view(self, er_schema):
        """Both halves of the condition matter: a figure whose source says `intent`
        but carries no index has nothing to look up, and reading the intent list at
        `None` would take the last intent and attribute it to the wrong figure."""
        from chartgen.interfaces.figure import Source

        rotation = figure(BAR, source=Source(kind="rotation"))
        assert C.build(rotation, er_schema) == C.describe(rotation, er_schema)
        loose = figure(BAR, source=Source(kind="intent", intent_index=None))
        assert C.build(loose, er_schema) == C.describe(loose, er_schema)

    def test_an_intent_figure_says_what_the_image_cannot(self, er_schema):
        from chartgen.interfaces.figure import Source

        built = figure(BAR, source=Source(kind="intent", intent_index=0))
        text = C.build(built, er_schema)
        assert er_schema.intents[0].sentence.lower()[:20] in text.lower()
        assert er_schema.data_context[:20] in text

    def test_counting_rows_names_no_column(self, er_schema):
        """The counting aggregate already says what it counts. Given a column name as
        well it reads "the number of records records", on the axis as in the caption."""
        from chartgen.interfaces.table import aggregate_phrase

        assert aggregate_phrase("COUNT", "") == "the number of records"
        counted = Binding("funnel", dims=("hospital",), aggregate="COUNT")
        assert "records records" not in C.describe(figure(counted), er_schema)

    def test_two_measures_read_as_one_against_the_other(self, er_schema):
        pair = Binding("scatter", measures=("wait_minutes", "cost"), aggregate="NONE")
        assert C.describe(figure(pair), er_schema) == "Average wait against Cost per visit."

    def test_a_derived_figure_says_how_its_views_relate(self, er_schema):
        got = C.describe(figure(BAR, relation="small_multiples"), er_schema)
        assert "one panel per category" in got


class TestWhereItComesFrom:
    def test_a_figure_built_from_an_intent_says_what_the_data_was_collected_for(
            self, er_schema):
        spec = figure(BAR, source=Source("intent", intent_index=0))
        got = C.build(spec, er_schema)
        assert er_schema.intents[0].sentence.lower()[:20] in got.lower()
        assert er_schema.data_context in got

    def test_that_is_the_part_no_reader_could_get_off_the_image(self, er_schema):
        """A caption a model can write from the figure alone teaches it nothing."""
        spec = figure(BAR, source=Source("intent", intent_index=0))
        assert C.build(spec, er_schema) != C.describe(spec, er_schema)
        assert len(C.build(spec, er_schema)) > len(C.describe(spec, er_schema))

    def test_any_other_figure_is_described_by_its_own_view(self, er_schema):
        spec = figure(BAR, source=Source("rotation"))
        assert C.build(spec, er_schema) == C.describe(spec, er_schema)

    def test_every_figure_of_a_batch_gets_one(self, er_table, er_schema):
        from chartgen.config import Config
        from chartgen.s02_figure.compose import compose

        figures = compose(er_table, er_schema, 20260816, Config.load())
        assert figures and all(f.caption for f in figures)

    def test_the_ones_built_from_an_intent_are_the_ones_that_say_more(self, er_table,
                                                                      er_schema):
        from chartgen.config import Config
        from chartgen.s02_figure.compose import compose

        figures = compose(er_table, er_schema, 20260816, Config.load())
        built = [f for f in figures if f.source.kind == "intent"]
        rest = [f for f in figures if f.source.kind == "rotation"]
        assert built and rest
        assert min(len(f.caption) for f in built) > max(len(f.caption) for f in rest)

    def test_it_reaches_the_record_that_the_exporter_reads(self, er_table, er_schema,
                                                          tmp_path):
        """The exporter reads the record and nothing upstream, so a caption that did
        not survive the journey is a target that is silently empty."""
        from chartgen.config import Config
        from chartgen.s02_figure.compose import compose
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default
        from chartgen.s04_record.selfcheck import finish
        from chartgen.s05_output.export import build

        spec = compose(er_table, er_schema, 20260816, Config.load())[0]
        record = finish(render(spec, default(), tmp_path), spec)
        assert record.caption == spec.caption
        assert build(record).caption == spec.caption


class TestTheSourceLine:
    """A source line on a real page names a body and a collection. The scenario title
    is the question the page answers and runs to a sentence: sixty of ninety-six
    source lines were cut short on the page, most of them mid-word."""

    def test_it_names_the_pool_entry_when_there_is_one(self, er_schema):
        from dataclasses import replace

        from chartgen.interfaces.table import Origin
        from chartgen.s02_figure.title import source_line

        schema = replace(er_schema, origin=Origin(domain_id="dom_001",
                                                  domain="Emergency department waits",
                                                  topic="Hospital Operations",
                                                  complexity_tier="simple"))
        assert source_line(schema) == ("Source: Hospital Operations, "
                                       "Emergency department waits")

    def test_it_falls_back_to_the_scenario_title(self, er_schema):
        from chartgen.s02_figure.title import source_line

        assert er_schema.origin.topic == ""
        assert source_line(er_schema).startswith("Source: ")
        assert er_schema.scenario_title[:20] in source_line(er_schema)

    def test_a_long_one_is_cut_here_rather_than_on_the_page(self, er_schema):
        from dataclasses import replace

        from chartgen.s02_figure.title import SOURCE_LIMIT, source_line

        schema = replace(er_schema, scenario_title="Emergency department " * 20)
        line = source_line(schema)
        assert len(line) <= SOURCE_LIMIT + len("Source: ") + 1
        assert line.endswith("…")
