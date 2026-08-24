"""The diagram page and the terminal summary the data stage writes for every schema.

Not on the production path, but this is what a person looks at when a run seems
wrong, so it has to keep working.
"""

import pandas as pd
import pytest

from chartgen import report
from chartgen.common import serde
from chartgen.interfaces.table import FactTable, TableSchema


@pytest.fixture
def schema() -> TableSchema:
    return serde.sample("TableSchema")


@pytest.fixture
def table(schema) -> FactTable:
    return FactTable(schema.scenario_id, pd.DataFrame({
        "hospital": ["Mercy General", "St. Luke's", "Riverside"],
        "wait_minutes": [42.3, 35.8, 28.1]}))


class TestDiagrams:
    def test_a_hierarchy_becomes_an_edge(self, schema):
        assert "hospital --> department" in report.hierarchy(schema)

    def test_a_derived_calendar_field_is_a_dashed_edge(self, schema):
        assert "visit_date -.-> month" in report.hierarchy(schema)

    def test_a_measure_dependency_becomes_an_edge(self, schema):
        assert "wait_minutes --> cost" in report.dependencies(schema)

    def test_an_intent_points_at_the_columns_it_binds(self, schema):
        assert "i0 --> hospital" in report.intents(schema)

    def test_the_page_says_what_is_drawable_and_how_dense_the_table_is(self, schema):
        text = report.markdown(schema)
        assert "| comparison | yes |" in text and "| process | no |" in text
        assert "rows per cell" in text

    def test_the_page_lands_beside_the_schema(self, schema, tmp_path):
        out = report.page(schema, tmp_path / "s000" / "schema.md")
        assert out.read_text(encoding="utf-8").startswith(f"# {schema.scenario_title}")


class TestTheRecordAndTargetViews:
    """The two summaries a person reads after a run: what came out, and what one row
    of it looks like once it is a training target."""

    def record(self, tmp_path):
        from chartgen.interfaces.figure import Binding, FigureSpec, PanelSpec
        from chartgen.s01_data.author import compose
        from chartgen.config import Config
        from chartgen.s02_figure.project import project
        from chartgen.s03_render.render import render
        from chartgen.s03_render.style import default
        from chartgen.s04_record.selfcheck import finish
        import json
        from pathlib import Path as P

        payload = json.loads((P(__file__).resolve().parents[1] / "samples"
                              / "er_scenario.json").read_text(encoding="utf-8"))
        table, schema = compose(payload, scenario_id="er", seed=20260816,
                                config=Config.load())
        binding = Binding("bar", dims=("hospital",), measures=("wait_minutes",),
                          aggregate="AVG", key_sources=("axis_tick",))
        view = project(table.df, binding, schema)
        spec = FigureSpec("f01", "er", (PanelSpec("p0", (view,)),),
                          column_units={"wait_minutes": "minutes"},
                          caption="Average wait by hospital.")
        return finish(render(spec, default(), tmp_path), spec)

    def test_the_target_summary_counts_every_target_and_shows_one_row(self, tmp_path):
        record = self.record(tmp_path)
        text = report.target_summary([record])
        assert "grounded_table" in text and "key_source" in text
        assert f"| grounded_table | {len(record.marks)} |" in text
        first = record.marks[0]
        assert first.key[0] in text
        assert "caption" in text and record.caption[:20] in text

    def test_the_target_summary_survives_a_record_with_nothing_in_it(self, tmp_path):
        from dataclasses import replace

        empty = replace(self.record(tmp_path), marks=())
        text = report.target_summary([empty])
        assert "| grounded_table | 0 |" in text

    def test_the_record_summary_reports_readability_by_type(self, tmp_path):
        text = report.record_summary([self.record(tmp_path)])
        assert "bar" in text


class TestTerminalViews:
    def test_the_tree_indents_a_child_under_its_parent(self, schema):
        lines = report.tree(schema).splitlines()
        assert "  |- hospital (3)" in lines and "    `- department (4)" in lines

    def test_the_summary_carries_the_scenario_the_intents_and_the_table_size(
            self, table, schema):
        text = report.summary(table, schema)
        assert schema.scenario_title in text
        assert schema.intents[0].sentence in text
        assert f"{table.n_rows} rows" in text


class TestTheReadableViewNamesWhereTheScenarioCameFrom:
    """A batch is a sample of the domain pool, and the scenario title is written by
    the model: it names neither the sub-topic nor the tier. Without the pool entry
    beside it, a batch cannot be described as covering one part of the pool."""

    def with_origin(self, er_schema):
        from dataclasses import replace

        from chartgen.interfaces.table import Origin

        return replace(er_schema, origin=Origin(
            "dom_042", "ICU bed turnover", "Hospital bed management",
            subject="health and care", register="operational",
            complexity_tier="complex"))

    def test_the_markdown_names_the_pool_entry(self, er_schema):
        from chartgen import report

        text = report.markdown(self.with_origin(er_schema))
        assert "dom_042" in text and "ICU bed turnover" in text and "complex" in text
        assert "health and care" in text and "operational" in text, (
            "the register is the axis a topic name cannot stand in for")

    def test_the_terminal_summary_names_it_too(self, er_table, er_schema):
        from chartgen import report

        text = report.summary(er_table, self.with_origin(er_schema))
        assert "ICU bed turnover" in text

    def test_a_hand_written_scenario_has_no_pool_entry_and_says_nothing(
            self, er_table, er_schema):
        """`--payload` runs a hand-written answer, which was drawn from no pool."""
        from chartgen import report

        assert er_schema.origin.domain == ""
        assert "Drawn from" not in report.markdown(er_schema)
