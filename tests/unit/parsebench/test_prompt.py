"""The text sent with the page image. It is half the cache key, so it is pinned."""

import prompt
import schema
import vocabulary


def test_the_whole_vocabulary_is_in_the_prompt():
    text = prompt.user_prompt()
    assert all(key in text for key in vocabulary.KEYS)


def test_every_gap_item_a_suggestion_can_name_is_explained():
    text = prompt.user_prompt()
    assert all(f"  {gap} = " in text for gap in schema.GAP_ITEMS)


def test_every_generality_verdict_is_explained():
    text = prompt.user_prompt()
    assert all(f"  {name} = " in text for name in schema.GENERALITY)


def test_the_page_values_go_in():
    """They are what makes the answer about this page rather than about pages."""
    assert "50  ·  27" in prompt.user_prompt(("50", "27"))


def test_a_page_with_no_rules_says_so_rather_than_showing_an_empty_list():
    assert "none recorded for this page" in prompt.user_prompt(())


def test_the_re_ask_says_why_an_empty_answer_is_not_one():
    assert "spot-check points" in prompt.RETRY_NOTE
