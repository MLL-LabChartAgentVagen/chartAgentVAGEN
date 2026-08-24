"""Reading and overriding configuration.

Every stage reads its settings through this one object, and a setting that silently
does not arrive is an ablation that quietly did not happen. The dotted paths are
where that goes wrong: a path that runs through a leaf, and a path that has to be
created on the way down.
"""

import pytest

from chartgen.config import Config


class TestReading:
    def test_a_dotted_path_walks_the_nested_mapping(self):
        config = Config({"figure": {"k_max": 8, "density": {"band": "sparse"}}})
        assert config.get("figure.k_max") == 8
        assert config.get("figure.density.band") == "sparse"

    def test_a_missing_key_gives_the_default(self):
        assert Config({"a": {"b": 1}}).get("a.c", "fallback") == "fallback"
        assert Config({}).get("a.b.c", 7) == 7

    def test_a_path_that_runs_through_a_leaf_gives_the_default(self):
        """`figure.k_max.band` names nothing: the walk has to stop at the number
        rather than ask it for a key."""
        assert Config({"figure": {"k_max": 8}}).get("figure.k_max.band", "none") == "none"

    def test_the_default_file_reads(self):
        config = Config.load()
        assert config.get("figure.k_max") and config.get("output.dir")


class TestOverriding:
    def test_setting_a_leaf_leaves_its_neighbours_alone(self):
        config = Config({"figure": {"k_max": 8, "pages": 1}})
        config.set("figure.k_max", 3)
        assert config.values == {"figure": {"k_max": 3, "pages": 1}}

    def test_setting_a_path_that_does_not_exist_yet_creates_it(self):
        config = Config({})
        config.set("render.style_overrides.palette", "grayscale")
        assert config.values == {"render": {"style_overrides": {"palette": "grayscale"}}}
        assert config.get("render.style_overrides.palette") == "grayscale"

    def test_an_assignment_is_read_as_yaml(self):
        config = Config({}).override(["figure.k_max=8", "render.degradation=false",
                                      "output.targets=[caption, spot_check]"])
        assert config.get("figure.k_max") == 8
        assert config.get("render.degradation") is False
        assert config.get("output.targets") == ["caption", "spot_check"]

    def test_an_assignment_with_no_value_is_an_empty_setting(self):
        assert Config({}).override(["a.b="]).get("a.b") is None

    @pytest.mark.parametrize("dotted", ["a", "a.b", "a.b.c.d"])
    def test_what_was_set_is_what_comes_back(self, dotted):
        config = Config({}).set(dotted, 42)
        assert config.get(dotted) == 42
