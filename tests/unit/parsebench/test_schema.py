"""The structured-output contract."""

from llmkit.providers import check_strict

import schema


def test_it_is_accepted_for_structured_output():
    check_strict(schema.SCHEMA)


def test_the_component_enum_is_the_vocabulary():
    import vocabulary
    key = schema.SCHEMA["properties"]["components"]["items"]["properties"]["key"]
    assert key["enum"] == list(vocabulary.KEYS)


def test_a_component_cannot_be_reported_without_evidence():
    """A key with no evidence is a claim, and claims cannot be summed into a table."""
    item = schema.SCHEMA["properties"]["components"]["items"]
    assert item["required"] == ["key", "figure_id", "evidence"]


def test_the_heading_is_split_into_the_five_things_a_generator_must_produce():
    heading = schema.SCHEMA["properties"]["figures"]["items"]["properties"]["heading"]
    assert set(heading["required"]) == {"figure_number", "title", "subtitle",
                                        "unit_text", "placement"}
    assert "beside" in heading["properties"]["placement"]["enum"]


def test_an_other_type_has_a_place_to_be_named():
    figure = schema.SCHEMA["properties"]["figures"]["items"]
    assert "other" in figure["properties"]["type"]["enum"]
    assert "type_other" in figure["required"]


def test_a_spot_check_predicts_the_keys_that_address_its_value():
    item = schema.SCHEMA["properties"]["spot_checks"]["items"]
    assert set(item["required"]) == {"value", "figure_id", "mark",
                                     "printed_on_figure", "addressing_keys"}


def test_a_suggestion_must_name_its_ablation_row_and_how_general_it_is():
    suggestion = schema.SCHEMA["properties"]["suggestions"]["items"]
    assert "new_ablation_row" in suggestion["required"]
    assert suggestion["properties"]["generality"]["enum"] == list(schema.GENERALITY)


def test_the_title_change_is_a_gap_item_a_suggestion_can_name():
    assert "P7" in schema.GAP_ITEMS


def test_the_four_steps_are_the_four_the_metric_has():
    assert sorted(schema.STEPS) == [1, 2, 3, 4]
    assert schema.SCHEMA["properties"]["hardest_step"]["enum"] == [1, 2, 3, 4]
