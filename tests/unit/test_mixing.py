"""What each source of a training set may be asked for."""

import pytest

from chartgen.config import Config
from chartgen.s05_output.mixing import Mix, MixError, Portion, from_config

EVERY = ("grounded_table", "spot_check", "mark_locate", "mark_read", "drilldown",
         "page_elements", "legend_binding", "caption")


class TestWhatASourceCanAnswer:
    def test_generated_figures_answer_every_target(self):
        assert set(Portion("generated", 1.0).targets(EVERY)) == set(EVERY)

    def test_a_real_chart_is_not_asked_for_a_region_it_never_had(self):
        """Its annotations carry a key and a value for every point and a box for
        none of them."""
        got = Portion("real_charts", 1.0).targets(EVERY)
        assert set(got) == {"grounded_table", "caption"}
        assert got["grounded_table"] == ("key", "values")

    def test_a_real_page_layout_answers_only_the_page_element_boxes(self):
        assert set(Portion("real_layouts", 1.0).targets(EVERY)) == {"page_elements"}


class TestTheMix:
    def test_shares_are_proportions_of_the_whole(self):
        mix = Mix((Portion("generated", 3.0), Portion("real_charts", 1.0)))
        assert mix.share("generated") == pytest.approx(0.75)
        assert mix.share("real_layouts") == 0.0

    def test_a_target_no_source_can_answer_is_an_error(self):
        mix = Mix((Portion("real_charts", 1.0),))
        with pytest.raises(MixError) as caught:
            mix.check(EVERY)
        assert "mark_read" in str(caught.value)

    def test_a_mix_that_covers_its_targets_passes(self):
        mix = Mix((Portion("generated", 0.8), Portion("real_charts", 0.2)))
        mix.check(EVERY)

    def test_an_empty_or_negative_mix_is_refused(self):
        with pytest.raises(MixError):
            Mix(())
        with pytest.raises(MixError):
            Mix((Portion("generated", -1.0),))

    def test_shares_that_add_up_to_nothing_are_refused(self):
        """Zero everywhere is not a mix: `share` would divide by it, and a set with
        no source in it is not a smaller training set but an empty one."""
        with pytest.raises(MixError):
            Mix((Portion("generated", 0.0), Portion("real_charts", 0.0)))

    def test_a_run_of_this_repository_alone_is_all_generated(self):
        assert from_config(Config.load()).share("generated") == 1.0
