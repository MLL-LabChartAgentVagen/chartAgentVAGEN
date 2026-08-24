"""The fault injector that the review pages quote.

A tool that reports how many injected faults the tests caught is only worth reading
if the faults it injects are real. Changing a word inside a docstring changes
nothing, so a mutation there always survives and reads as a gap in the suite when it
is a gap in the tool.
"""

from pathlib import Path

from tools import mutation


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "sample.py"
    path.write_text(text, encoding="utf-8")
    return path


class TestWhatCountsAsCode:
    def test_a_comparison_in_code_is_mutated(self, tmp_path):
        path = write(tmp_path, "def f(a, b):\n    return a >= b\n")
        picks = mutation.candidates(path)
        assert [(n, after.strip()) for n, _, after, _ in picks] == [(2, "return a >  b")]

    def test_nothing_inside_a_docstring_is_mutated(self, tmp_path):
        path = write(tmp_path, '"""A and B, all of them, not one.\n\nmin and max.\n"""\n'
                               "value = 1\n")
        assert mutation.candidates(path) == []

    def test_nothing_inside_a_comment_is_mutated(self, tmp_path):
        path = write(tmp_path, "value = 1  # keep this and that, all of it\n")
        assert mutation.candidates(path) == []

    def test_the_text_of_a_message_is_left_alone_but_its_code_is_not(self, tmp_path):
        path = write(tmp_path, 'def f(a, b):\n'
                               '    if a >= b:\n'
                               '        raise ValueError(f"{a} is not below {b}")\n')
        lines = {n for n, _, _, _ in mutation.candidates(path)}
        assert lines == {2}, "only the comparison, not the words in the message"

    def test_a_line_holding_both_a_string_and_a_comparison_keeps_the_comparison(
            self, tmp_path):
        path = write(tmp_path, 'def f(a):\n    return "not here" if a >= 1 else ""\n')
        picks = mutation.candidates(path)
        assert any("a >  1" in after for _, _, after, _ in picks)
        assert not any('"not  here"' in after for _, _, after, _ in picks)


class TestEveryTargetIsReal:
    def test_each_module_named_exists_and_names_tests_that_exist(self):
        root = Path(mutation.__file__).resolve().parents[1]
        for module, tests in mutation.COVERED_BY.items():
            assert (root / "src" / "chartgen" / module).exists(), module
            for name in tests:
                assert (root / "tests" / "unit" / name).exists(), (module, name)

    def test_every_pipeline_file_of_any_size_is_covered(self):
        """A file nobody injects faults into is a file the report says nothing about."""
        root = Path(mutation.__file__).resolve().parents[1] / "src" / "chartgen"
        missing = []
        for path in root.rglob("*.py"):
            if path.name == "__init__.py" or "__pycache__" in str(path):
                continue
            name = str(path.relative_to(root))
            if name not in mutation.COVERED_BY and len(
                    path.read_text(encoding="utf-8").splitlines()) > 40:
                missing.append(name)
        assert not missing, missing
