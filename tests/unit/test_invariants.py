"""Static checks on the shape of the code itself.

Some of what the design promises is not a property of any one run: it is a property
of which module reaches which. A rule like "only one file in view selection may call
a model" cannot be tested by calling it -- it has to be read off the imports, or it
goes quietly untrue the first time someone needs an answer in a hurry.
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "chartgen"


def imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            out.add(node.module or "")
        elif isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
    return out


def files(package: str) -> list[Path]:
    return sorted(p for p in (SRC / package).rglob("*.py") if p.name != "__init__.py")


class TestWhereAModelIsCalled:
    def test_only_the_two_named_files_reach_a_model(self):
        """The pipeline makes two calls: the data stage writes the data, view
        selection writes the words. A third would be a third thing to reproduce."""
        callers = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*.py")
                   if any("llmkit" in m for m in imports_of(p))}
        assert callers == {"s01_data/author.py", "s02_figure/title.py", "cli.py"}

    def test_nothing_after_view_selection_reaches_a_model(self):
        for package in ("s03_render", "s04_record", "s05_output", "registry", "common"):
            for path in files(package):
                assert not any("llmkit" in m for m in imports_of(path)), path


class TestWhereRandomnessLives:
    def test_only_these_seven_files_draw_a_random_number(self):
        """Everything else is a rule: the same input and seed must give the same
        output, and a stray draw is how that stops being true. Every one of these
        derives its stream from the root seed, so none of them reads shared state
        and the order they run in cannot change what any of them produces."""
        drawing = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*.py")
                   if any("rng" in module for module in imports_of(p))}
        assert drawing == {"s01_data/pool.py", "s01_data/engine.py",
                           "s01_data/author.py", "s02_figure/compose.py",
                           "s02_figure/project.py", "s03_render/style.py",
                           "s03_render/degrade.py"}

    def test_no_module_reads_the_global_random_state(self):
        for path in SRC.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "np.random.seed" not in text, path
            assert "random.random(" not in text, path


class TestLayering:
    def test_no_stage_imports_another_stage(self):
        """Stages talk through the interfaces. The one exception is the record
        stage's checks, which the reward path deliberately shares rather than
        copies."""
        allowed = {("s05_output/verify.py", "s04_record")}
        for package in ("s01_data", "s02_figure", "s03_render", "s04_record", "s05_output"):
            for path in files(package):
                name = path.relative_to(SRC).as_posix()
                for module in imports_of(path):
                    for other in ("s01_data", "s02_figure", "s03_render",
                                  "s04_record", "s05_output"):
                        if other == package or other not in module:
                            continue
                        assert (name, other) in allowed, f"{name} imports {module}"

    def test_the_exporter_reads_the_record_and_nothing_upstream(self):
        """A record that needed a stage module to be read would not be self-sufficient,
        and a saved batch could then only be interpreted by the code that made it."""
        modules = imports_of(SRC / "s05_output" / "export.py")
        assert not [m for m in modules if ".s0" in m or m.startswith("s0")]

    def test_the_feasibility_rules_cannot_see_data(self):
        """They run before a row exists and again after; both answers come from the
        same declarations, so they cannot drift apart."""
        text = (SRC / "registry" / "conditions.py").read_text(encoding="utf-8")
        assert "pandas" not in text and "FactTable" not in text
        assert "import numpy" not in text


class TestOneImplementation:
    def test_the_self_check_and_the_reward_call_the_same_function(self):
        """Two copies of this arithmetic would eventually disagree, and silently."""
        for name in ("s04_record/selfcheck.py", "s05_output/verify.py"):
            text = (SRC / name).read_text(encoding="utf-8")
            assert "check_mark" in text and "from ..common.readback import" in text

    def test_the_readability_rule_lives_in_one_place(self):
        callers = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*.py")
                   if "channels" in " ".join(imports_of(p))}
        assert callers <= {"registry/conditions.py", "s04_record/readable.py",
                           "s04_record/selfcheck.py", "s05_output/export.py",
                           "s05_output/verify.py", "common/readback.py"}

    def test_every_chart_type_has_exactly_one_drawing_branch(self):
        from chartgen.registry.charts import CHARTS
        from chartgen.s03_render.draw import DRAWERS

        assert set(CHARTS) == set(DRAWERS)


class TestStyleStaysStyle:
    def test_a_series_marker_is_never_a_different_mark_shape(self):
        """A diamond and a dot are both a point and both stay measurable. A sector
        or a cell would change whether the value can be read at all, which is what
        makes it a chart type rather than a style."""
        from chartgen.interfaces.style import STYLE_DOMAINS
        from chartgen.registry.charts import SHAPE_VALUE_KEYS

        markers = {m for value in STYLE_DOMAINS["series_marks"].domain if value
                   for m in value}
        assert markers and not markers & set(SHAPE_VALUE_KEYS)

    def test_the_column_carried_by_colour_is_not_a_style_setting(self):
        """If style chose it, restyling a figure would change its keys and the
        restyling self-check would have nothing left to compare."""
        from chartgen.interfaces.figure import Binding
        from chartgen.interfaces.style import STYLE_DOMAINS

        assert "colour_group" in Binding.__dataclass_fields__
        assert "colour_group" not in STYLE_DOMAINS

    def test_where_a_key_segment_is_read_from_is_not_a_style_setting(self):
        from chartgen.interfaces.figure import Binding
        from chartgen.interfaces.style import STYLE_DOMAINS

        assert "key_sources" in Binding.__dataclass_fields__
        assert not any("key" in name for name in STYLE_DOMAINS)
