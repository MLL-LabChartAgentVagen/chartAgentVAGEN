"""The fixed component vocabulary: one definition, two renderings."""

import vocabulary


def test_keys_are_unique():
    assert len(vocabulary.KEYS) == len(set(vocabulary.KEYS)) == len(vocabulary.VOCABULARY)


def test_every_key_reaches_the_prompt():
    block = vocabulary.prompt_block()
    assert all(f"  {key} = " in block for key in vocabulary.KEYS)


def test_every_component_names_the_spec_line_behind_its_verdict():
    assert all(c.basis.strip() for c in vocabulary.VOCABULARY)


def test_nothing_is_left_unverified():
    """`ours` is read off the spec before any page is seen, so it is a bool."""
    assert all(isinstance(c.ours, bool) for c in vocabulary.VOCABULARY)



def test_every_chart_type_the_model_may_answer_has_an_ours_verdict():
    """The same question the components are asked, asked of the type list."""
    import schema
    assert set(schema.CHART_TYPES) == set(vocabulary.CHART_TYPE_OURS)
    assert all(basis.strip() for _, basis in vocabulary.CHART_TYPE_OURS.values())
