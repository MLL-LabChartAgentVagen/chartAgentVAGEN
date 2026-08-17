"""The four declaration methods: argument checks, isolated execution, and the schema.

Everything that must be caught before generation is here. When an argument is
wrong the message has to name the column, the argument and the reason, because
that text is fed straight back to the model.
"""

import json
from pathlib import Path

import pytest

from chartgen.s01_data import declare as D
from chartgen.s01_data.declare import DeclarationError

SAMPLE = json.loads((Path("tests/samples/er_scenario.json")).read_text(encoding="utf-8"))

MINIMAL = """
dim("site", ["A", "B", "C"], group="place")
dim("grade", ["Low", "High"], ordered="ordinal", group="grade")
measure("units", "poisson(30)", unit="units", additive=True)
measure("score", "clip(units / 10, 1, 5)", unit="points", additive=False)
emit(200)
"""


@pytest.fixture
def er() -> D.Script:
    return D.run(SAMPLE["script"])


class TestTheScriptRuns:
    def test_the_worked_example_declares_three_dimensions(self, er):
        assert [d.name for d in er.dims] == ["hospital", "department", "severity"]

    def test_it_declares_one_time_column(self, er):
        assert er.time.name == "visit_date" and er.time.freq == "daily"

    def test_it_declares_three_measures_with_units_and_additivity(self, er):
        assert [(m.name, m.unit, m.additive) for m in er.measures] == [
            ("wait_minutes", "minutes", True),
            ("cost", "USD", True),
            ("satisfaction", "points", False),
        ]

    def test_emit_fixes_the_row_count(self, er):
        assert er.n_rows == 900

    def test_the_hierarchy_and_the_ordinal_flag_survive(self, er):
        assert er.dim("department").parent == "hospital"
        assert er.dim("severity").ordered == "ordinal"

    def test_conditional_weights_are_kept_per_parent_value(self, er):
        assert er.dim("department").weights["Riverside"] == (0.30, 0.30, 0.15, 0.25)


class TestArgumentChecks:
    def test_a_dimension_needs_at_least_two_values(self):
        with pytest.raises(DeclarationError, match="values"):
            D.run('dim("x", ["only"])\nemit(10)')

    def test_repeated_values_in_one_dimension_are_rejected(self):
        with pytest.raises(DeclarationError, match="repeated"):
            D.run('dim("x", ["A", "A", "B"])\nemit(10)')

    def test_weights_must_be_as_many_as_values(self):
        with pytest.raises(DeclarationError, match="weights"):
            D.run('dim("x", ["A", "B", "C"], weights=[0.5, 0.5])\nemit(10)')

    def test_conditional_weights_must_cover_every_parent_value(self):
        script = ('dim("p", ["A", "B"])\n'
                  'dim("c", ["u", "v"], parent="p", weights={"A": [0.5, 0.5]})\nemit(10)')
        with pytest.raises(DeclarationError, match="B"):
            D.run(script)

    def test_a_parent_must_be_declared_first(self):
        with pytest.raises(DeclarationError, match="hospital"):
            D.run('dim("department", ["a", "b"], parent="hospital")\nemit(10)')

    def test_ordered_takes_only_ordinal_or_stage(self):
        with pytest.raises(DeclarationError, match="ordered"):
            D.run('dim("x", ["A", "B"], ordered="sorted")\nemit(10)')

    def test_two_columns_cannot_share_a_name(self):
        with pytest.raises(DeclarationError, match="x"):
            D.run('dim("x", ["A", "B"])\nmeasure("x", "gaussian(0,1)", unit="u", '
                  'additive=True)\nemit(10)')

    def test_a_column_cannot_take_a_derived_calendar_name(self):
        with pytest.raises(DeclarationError, match="month"):
            D.run('dim("month", ["Jan", "Feb"])\ntime("d", start="2024-01-01", '
                  'end="2024-06-30", freq="daily")\nemit(10)')

    def test_only_one_time_column_is_allowed(self):
        with pytest.raises(DeclarationError, match="time column"):
            D.run('time("a", start="2024-01-01", end="2024-02-01", freq="daily")\n'
                  'time("b", start="2024-01-01", end="2024-02-01", freq="daily")\nemit(10)')

    def test_the_time_window_must_run_forward(self):
        with pytest.raises(DeclarationError, match="start"):
            D.run('time("d", start="2024-06-30", end="2024-01-01", freq="daily")\nemit(10)')

    def test_the_frequency_is_one_of_three(self):
        with pytest.raises(DeclarationError, match="freq"):
            D.run('time("d", start="2024-01-01", end="2024-06-30", freq="hourly")\nemit(10)')

    def test_a_measure_must_declare_its_unit_and_additivity(self):
        with pytest.raises(DeclarationError, match="additive"):
            D.run('measure("m", "gaussian(0, 1)", unit="u")\nemit(10)')

    def test_a_measure_expression_is_parsed_at_declaration_time(self):
        with pytest.raises(DeclarationError, match="does not parse"):
            D.run('measure("m", "gaussian(0, ", unit="u", additive=True)\nemit(10)')

    def test_emit_must_be_called(self):
        with pytest.raises(DeclarationError, match="emit"):
            D.run('dim("x", ["A", "B"])')

    def test_emit_cannot_be_called_twice(self):
        with pytest.raises(DeclarationError, match="emit"):
            D.run('dim("x", ["A", "B"])\nemit(10)\nemit(20)')


class TestHardConstraints:
    def test_two_dimension_groups_are_required(self):
        script = ('dim("p", ["A", "B"])\ndim("c", ["u", "v"], parent="p")\n'
                  'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                  'measure("n", "gaussian(0,1)", unit="u", additive=True)\nemit(10)')
        with pytest.raises(DeclarationError, match="dimension groups"):
            D.run(script)

    def test_two_measures_are_required(self):
        with pytest.raises(DeclarationError, match="numeric columns"):
            D.run('dim("x", ["A", "B"], group="g")\ndim("y", ["u", "v"], group="h")\n'
                  'measure("m", "gaussian(0,1)", unit="u", additive=True)\nemit(10)')


class TestIsolatedExecution:
    def test_the_script_cannot_reach_the_interpreter(self):
        with pytest.raises(DeclarationError):
            D.run('__import__("os").system("echo hi")\nemit(10)')

    def test_a_call_to_an_undeclared_method_is_reported(self):
        with pytest.raises(DeclarationError, match="fact"):
            D.run('fact("x", 1)\nemit(10)')

    def test_the_failing_line_is_named(self):
        with pytest.raises(DeclarationError, match="line 2"):
            D.run('dim("x", ["A", "B"], group="g")\ndim("y", ["only"], group="h")\nemit(10)')


class TestSchemaFromDeclarations:
    """Declarations to a schema. No data is involved, which is what lets feasibility
    be decided before generation."""

    @pytest.fixture
    def schema(self, er):
        return D.to_schema(er, scenario_id="er_wait", title="T", context="C", intents=())

    def test_cardinality_comes_straight_from_the_declaration(self, schema):
        assert schema.column("hospital").cardinality == 3
        assert schema.column("department").cardinality == 4

    def test_the_time_column_carries_its_point_count(self, schema):
        assert schema.column("visit_date").cardinality == 182     # 2024-01-01 .. 06-30

    def test_the_four_calendar_columns_are_derived(self, schema):
        derived = {c.name: c.cardinality for c in schema.columns if c.derived_from}
        assert derived == {"day_of_week": 7, "month": 6, "quarter": 2, "is_weekend": 2}

    def test_groups_follow_the_hierarchy_chain(self, schema):
        assert {g.name: g.columns for g in schema.groups} == {
            "entity": ("hospital", "department"),
            "triage": ("severity",),
            "calendar": ("visit_date", "day_of_week", "month", "quarter", "is_weekend"),
        }

    def test_a_group_defaults_to_the_root_of_its_chain(self):
        script = D.run('dim("p", ["A", "B"])\ndim("c", ["u", "v"], parent="p")\n'
                       'dim("k", ["x", "y"])\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(10)')
        schema = D.to_schema(script, scenario_id="s", title="T", context="C", intents=())
        assert {g.name: g.columns for g in schema.groups} == {"p": ("p", "c"), "k": ("k",)}

    def test_dependencies_are_read_out_of_the_expressions(self, schema):
        assert schema.dependencies == (("wait_minutes", "cost"),
                                       ("wait_minutes", "satisfaction"))

    def test_measures_keep_unit_and_additivity(self, schema):
        assert schema.column("cost").unit == "USD" and schema.column("cost").additive
        assert schema.column("satisfaction").additive is False

    def test_the_row_count_comes_from_emit(self, schema):
        assert schema.n_rows == 900

    def test_a_calendar_field_with_one_value_is_not_a_column(self):
        """On a weekly axis every point is a Monday, so two calendar fields are constant."""
        script = D.run('dim("a", ["A", "B"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                       'time("wk", start="2023-01-02", end="2024-06-24", freq="weekly")\n'
                       'measure("m", "gaussian(0,1)", unit="u", additive=True)\n'
                       'measure("n", "m * 2", unit="u", additive=True)\nemit(300)')
        schema = D.to_schema(script, scenario_id="s", title="T", context="C", intents=())
        assert [c.name for c in schema.columns if c.derived_from] == ["month", "quarter"]

    def test_a_schema_with_no_time_column_has_no_calendar_group(self):
        schema = D.to_schema(D.run(MINIMAL), scenario_id="s", title="T", context="C",
                             intents=())
        assert not schema.times and all(c.derived_from is None for c in schema.columns)
