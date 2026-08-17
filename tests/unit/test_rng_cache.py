"""种子派生与内容哈希缓存：`(输入, 种子) -> 输出` 逐位可复现的两块地基。"""

from pathlib import Path

import numpy as np
import pytest

from chartgen.common import cache, rng
from chartgen.interfaces import io

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestSeedDerivation:
    def test_same_parts_give_the_same_stream(self):
        a = rng.derive(7, "er_wait", "s02", 3).random(5)
        b = rng.derive(7, "er_wait", "s02", 3).random(5)
        assert np.array_equal(a, b)

    def test_different_stage_gives_a_different_stream(self):
        a = rng.derive(7, "er_wait", "s02", 3).random(5)
        b = rng.derive(7, "er_wait", "s03", 3).random(5)
        assert not np.array_equal(a, b)

    def test_different_root_seed_gives_a_different_stream(self):
        assert not np.array_equal(rng.derive(7, "x").random(5), rng.derive(8, "x").random(5))

    def test_seeds_are_stable_across_processes(self):
        """不能用 Python 的 hash()——它每个进程加盐，跨进程不可复现。"""
        import subprocess
        import sys

        code = ("import sys; sys.path.insert(0, 'src');"
                "from chartgen.common import rng; print(rng.seed_of(7, 'er_wait', 's02', 3))")
        for _ in range(2):
            out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                                 text=True, check=True, cwd=REPO_ROOT)
            assert int(out.stdout) == rng.seed_of(7, "er_wait", "s02", 3)

    def test_the_derivation_itself_is_pinned(self):
        """改这个值等于作废全部已落盘的产物，所以它是有意钉死的。"""
        assert rng.seed_of(7, "er_wait", "s02", 3) == 6941357540799242452

    def test_deriving_twice_does_not_advance_a_shared_state(self):
        first = rng.derive(1, "a")
        first.random(100)
        assert rng.derive(1, "a").random(1) == pytest.approx(first := rng.derive(1, "a").random(1))
        assert first is not None

    def test_choice_is_reproducible(self):
        pick = lambda: rng.derive(3, "rotation").choice(["bar", "pie", "line"], size=4).tolist()
        assert pick() == pick()


class TestContentHash:
    def test_the_same_object_hashes_the_same(self):
        schema = io.sample("TableSchema")
        assert cache.content_hash(schema) == cache.content_hash(io.sample("TableSchema"))

    def test_a_changed_field_changes_the_hash(self):
        import dataclasses
        schema = io.sample("TableSchema")
        other = dataclasses.replace(schema, n_rows=901)
        assert cache.content_hash(schema) != cache.content_hash(other)

    def test_hash_is_hex_and_short_enough_for_a_path(self):
        h = cache.content_hash(io.sample("StyleVector"))
        assert len(h) == 16 and all(c in "0123456789abcdef" for c in h)

    def test_plain_values_hash_too(self):
        assert cache.content_hash({"a": [1, 2], "b": "x"}) == cache.content_hash({"b": "x", "a": [1, 2]})


class TestArtifactCache:
    def test_a_miss_builds_and_a_hit_reuses(self, tmp_path):
        from chartgen.interfaces.style import StyleVector

        calls = []

        def build() -> StyleVector:
            calls.append(1)
            return StyleVector(value_labels="all")

        store = cache.Store(tmp_path)
        first = store.get_or_build(StyleVector, "style", ["k"], build)
        second = store.get_or_build(StyleVector, "style", ["k"], build)
        assert first == second and len(calls) == 1

    def test_a_different_key_is_a_different_artifact(self, tmp_path):
        from chartgen.interfaces.style import StyleVector

        store = cache.Store(tmp_path)
        store.get_or_build(StyleVector, "style", ["a"], lambda: StyleVector(value_labels="all"))
        got = store.get_or_build(StyleVector, "style", ["b"], lambda: StyleVector(value_labels="none"))
        assert got.value_labels == "none"

    def test_disabling_the_cache_always_rebuilds(self, tmp_path):
        from chartgen.interfaces.style import StyleVector

        calls = []
        store = cache.Store(tmp_path, enabled=False)
        for _ in range(2):
            store.get_or_build(StyleVector, "style", ["k"],
                               lambda: (calls.append(1), StyleVector())[1])
        assert len(calls) == 2
