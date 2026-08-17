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
