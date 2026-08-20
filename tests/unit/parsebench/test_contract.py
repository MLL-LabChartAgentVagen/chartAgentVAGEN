"""The output contract: one module, and the schemas three models answer against.

These are checks on a definition, not on a run. They exist because the contract
is what makes three models' answers comparable, and a field that quietly loses
its domain -- an enum turned into free text, one of the two conclusion columns
dropped -- would not fail anywhere else until the reports had already been written.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "parsebench" / "tools"))

from contract import format as contract, vocabulary  # noqa: E402
from llmkit.providers import check_strict  # noqa: E402


class TestStructuredOutput:
    @pytest.mark.parametrize("schema", [contract.PAGE_SCHEMA, contract.FAILURE_SCHEMA])
    def test_both_schemas_are_accepted_for_structured_output(self, schema):
        check_strict(schema)

    @pytest.mark.parametrize("schema", [contract.PAGE_SCHEMA, contract.FAILURE_SCHEMA])
    def test_every_declared_field_is_required(self, schema):
        """No optional fields: a field that some models fill and others omit reads
        as a disagreement about the page."""
        def walk(node, path="schema"):
            if node.get("type") == "object":
                assert set(node.get("properties", {})) == set(node.get("required", ())), path
            for key, sub in node.get("properties", {}).items():
                walk(sub, f"{path}.{key}")
            if isinstance(node.get("items"), dict):
                walk(node["items"], f"{path}[]")

        walk(schema)


class TestValueDomains:
    def test_the_component_enum_is_the_vocabulary(self):
        key = contract.PAGE_SCHEMA["properties"]["components"]["items"]["properties"]["key"]
        assert key["enum"] == list(vocabulary.KEYS)

    def test_a_component_cannot_be_reported_without_evidence(self):
        item = contract.PAGE_SCHEMA["properties"]["components"]["items"]
        assert item["required"] == ["key", "figure_id", "evidence"]

    def test_the_heading_is_split_into_the_five_fields_a_generator_must_produce(self):
        heading = contract.PAGE_SCHEMA["properties"]["figures"]["items"]["properties"]["heading"]
        assert set(heading["properties"]) == {"figure_number", "title", "subtitle",
                                              "unit_text", "placement"}

    def test_other_must_be_named(self):
        figure = contract.PAGE_SCHEMA["properties"]["figures"]["items"]["properties"]
        assert "other" in figure["type"]["enum"] and "type_other" in figure


class TestTheTwoRules:
    """§T0 of the redo: every observation says which step it can change, and every
    suggestion answers two questions that are not on one scale."""

    @pytest.mark.parametrize("field", ["new_components", "suggestions"])
    def test_what_the_model_proposes_carries_affects(self, field):
        item = contract.PAGE_SCHEMA["properties"][field]["items"]
        assert "affects" in item["required"]
        assert item["properties"]["affects"]["items"]["enum"] == [1, 2, 3, 4]

    def test_the_vocabulary_keys_carry_affects_already_so_are_not_asked_for_it(self):
        component = contract.PAGE_SCHEMA["properties"]["components"]["items"]
        assert "affects" not in component["properties"]
        assert all(set(c.affects) <= {1, 2, 3, 4} for c in vocabulary.VOCABULARY)

    def test_a_suggestion_has_both_columns_and_they_stay_apart(self):
        item = contract.PAGE_SCHEMA["properties"]["suggestions"]["items"]
        assert {"score_effect", "capability_effect"} <= set(item["required"])

    def test_a_suggestion_names_the_ablation_row_it_adds(self):
        item = contract.PAGE_SCHEMA["properties"]["suggestions"]["items"]
        assert "new_ablation_row" in item["required"]

    def test_an_empty_affects_is_a_normal_answer(self):
        """`度量看不见它` is a finding about the metric, not a missing field."""
        assert "Empty array" in contract.PAGE_SCHEMA["properties"]["suggestions"]["items"][
            "properties"]["affects"]["description"]


class TestFailureAttribution:
    def test_the_model_never_decides_whether_a_point_passed(self):
        assert "passed" not in contract.FAILURE_SCHEMA["properties"]

    def test_the_form_is_computed_by_the_program_not_asked_of_the_model(self):
        assert "form" not in contract.FAILURE_SCHEMA["properties"]
        assert set(contract.FORMS) >= {"no_table", "label_unlinked", "value_off"}

    def test_every_mechanism_maps_back_onto_a_judgement_step(self):
        mapped = {k: s for k, s in contract.MECHANISM_STEP.items() if k != "other"}
        assert set(mapped.values()) <= set(contract.STEPS)

    def test_the_one_unmapped_mechanism_must_carry_a_note(self):
        assert contract.MECHANISM_STEP["other"] == 0
        assert "other" in contract.FAILURE_SCHEMA["properties"]["mechanism_note"]["description"]


class TestTheReports:
    """Three files, each section a set of tables, each table a row definition and
    its columns -- three models can only be compared per column."""

    def test_three_reports_each_with_a_file_of_its_own(self):
        assert [r.path for r in contract.REPORTS] == [
            "parsebench/reports/sample.md",
            "parsebench/reports/failures.md",
            "parsebench/reports/overview.md",
        ]

    def test_the_failure_analysis_is_one_report_not_a_directory_of_cases(self):
        columns = [c for s in contract.FAILURE_REPORT.sections for t in s.tables for c in t.columns]
        assert any("case_id" in c for c in columns), "an example is a column, not a file"

    def test_every_table_says_what_a_row_is_and_where_its_numbers_come_from(self):
        for report in contract.REPORTS:
            for section in report.sections:
                assert section.tables, section.title
                for table in section.tables:
                    assert table.row and table.columns
                    assert table.provenance in contract.PROVENANCE

    def test_the_two_conclusion_columns_survive_into_the_reports(self):
        """The one place the score and the capability could be silently merged."""
        for report in (contract.SAMPLE_REPORT, contract.OVERVIEW_REPORT):
            columns = [c for s in report.sections for t in s.tables for c in t.columns]
            assert "对分数" in columns and "对能力" in columns

    def test_the_numbers_a_model_must_not_be_the_source_of_are_listed(self):
        assert "通过率与 95% 区间" in contract.PROGRAM_ONLY

    def test_the_raw_answers_are_kept_per_model_and_page(self):
        assert "<model>" in contract.RAW_ANSWERS and "<page>" in contract.RAW_ANSWERS


class TestComparison:
    def test_every_aligned_quantity_names_the_decision_that_reads_it(self):
        """A column nothing consumes is a column that gets argued about for free."""
        for q in contract.SAMPLE_QUANTITIES + contract.FAILURE_QUANTITIES:
            assert q.unit and q.equal_when and q.consumer
            assert q.provenance in contract.PROVENANCE

    def test_the_scored_quantity_is_the_one_the_annotation_can_check(self):
        scored = [q for q in contract.SAMPLE_QUANTITIES if q.provenance == "rule_checkable"]
        assert [q.name for q in scored] == ["定位键预测"]

    def test_what_is_deliberately_not_aligned_is_written_down_with_a_reason(self):
        aligned = {q.name for q in contract.SAMPLE_QUANTITIES + contract.FAILURE_QUANTITIES}
        assert not (aligned & set(contract.NOT_ALIGNED))
        assert all(reason for reason in contract.NOT_ALIGNED.values())

    def test_every_agreement_class_has_a_decision(self):
        assert set(contract.AGREEMENT) == set(contract.DECISION)

    def test_only_a_unanimous_item_goes_straight_into_the_change_list(self):
        assert contract.DECISION["unanimous"] == "直接进改造清单"
        assert "不进清单" in contract.DECISION["single"]

    def test_the_shared_vocabulary_comes_with_its_own_controls(self):
        """The 65 keys are last round's product, so some of the agreement they
        produce is an artefact of the list. Both controls measure how much."""
        assert set(contract.CONTROLS) == {"词表外残差", "无词表对照"}
