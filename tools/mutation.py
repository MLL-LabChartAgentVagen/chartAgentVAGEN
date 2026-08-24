"""Injecting faults into the pipeline and asking whether the tests notice.

    python tools/mutation.py                # every target module
    python tools/mutation.py --module common/readback.py --limit 20

Coverage says a line ran. It does not say anything would have failed had that line
been wrong, and on this pipeline that is the question that matters: a box that is
off by two pixels raises nothing, produces a perfectly ordinary image, and poisons
every training target drawn from it.

So each run takes the source, changes one operator or constant, runs the tests that
cover that file, and records whether any of them failed. A mutant that survives is a
line the suite executes without checking -- which is a test to write, not a number to
report and forget.

The result is written as JSON for the review pages to read.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: What a run needs to import and to fixture from. Copied to a scratch directory so
#: the mutations are applied to a throwaway tree: the checkout keeps its own source
#: whatever happens to this process.
NEEDED = ("src", "tests", "tools", "configs", "pyproject.toml", "data/domains")

#: Which tests cover which file. A mutation is judged by the tests that claim to
#: cover it, not by the whole suite: the whole suite takes minutes, and a fault that
#: only a distant test catches is a fault this file's own tests are missing.
COVERED_BY: dict[str, tuple[str, ...]] = {
    "common/geometry.py": ("test_geometry.py", "test_render.py"),
    "common/readback.py": ("test_readback.py", "test_render.py", "test_shapes.py"),
    "registry/channels.py": ("test_channels.py", "test_record.py", "test_shapes.py"),
    "registry/charts.py": ("test_conditions.py", "test_shapes.py", "test_invariants.py"),
    "registry/conditions.py": ("test_conditions.py", "test_project.py"),
    "s01_data/declare.py": ("test_declare.py", "test_author.py"),
    "s01_data/engine.py": ("test_engine.py", "test_author.py"),
    "s01_data/expr.py": ("test_expr.py",),
    "s01_data/validate.py": ("test_validate.py", "test_author.py"),
    "s02_figure/project.py": ("test_project.py", "test_shapes.py"),
    "s02_figure/admit.py": ("test_admit.py", "test_compose.py"),
    "s02_figure/panel.py": ("test_panel.py", "test_compose.py"),
    "s02_figure/keys.py": ("test_project.py", "test_compose.py", "test_record.py"),
    "s02_figure/sampling.py": ("test_compose.py",),
    "s02_figure/compose.py": ("test_compose.py",),
    "s02_figure/caption.py": ("test_caption.py",),
    "s03_render/style.py": ("test_render.py", "test_shapes.py"),
    "s03_render/draw/canvas.py": ("test_render.py", "test_shapes.py"),
    "s03_render/draw/layout.py": ("test_layout.py", "test_render.py"),
    "s03_render/draw/rect.py": ("test_shapes.py", "test_render.py"),
    "s03_render/draw/point.py": ("test_shapes.py",),
    "s03_render/draw/frame.py": ("test_shapes.py", "test_render.py"),
    "s03_render/draw/labels.py": ("test_render.py",),
    "s03_render/draw/fit.py": ("test_render.py", "test_shapes.py"),
    "s03_render/draw/context.py": ("test_shapes.py", "test_render.py"),
    "s03_render/draw/sector.py": ("test_shapes.py",),
    "s03_render/draw/cell.py": ("test_shapes.py",),
    "s03_render/draw/boxlike.py": ("test_shapes.py",),
    "s03_render/page.py": ("test_page.py",),
    "s03_render/degrade.py": ("test_page.py", "test_record.py"),
    "s04_record/readable.py": ("test_record.py", "test_shapes.py"),
    "s04_record/selfcheck.py": ("test_record.py", "test_shapes.py"),
    "s04_record/merge.py": ("test_record.py", "test_page.py"),
    "s05_output/export.py": ("test_export.py", "test_page.py"),
    "s05_output/verify.py": ("test_export.py", "test_record.py"),
    "s05_output/mixing.py": ("test_mixing.py",),
    "s03_render/render.py": ("test_render.py", "test_shapes.py"),
    "s02_figure/title.py": ("test_compose.py", "test_caption.py"),
    "s01_data/pool.py": ("test_pool.py",),
    "s01_data/author.py": ("test_author.py",),
    "common/rng.py": ("test_rng_cache.py",),
    "common/cache.py": ("test_rng_cache.py",),
    "common/serde.py": ("test_serde.py",),
    "interfaces/figure.py": ("test_serde.py", "test_project.py", "test_compose.py"),
    "interfaces/record.py": ("test_serde.py", "test_record.py"),
    "interfaces/table.py": ("test_serde.py", "test_caption.py", "test_declare.py"),
    "interfaces/style.py": ("test_render.py", "test_serde.py"),
    "config.py": ("test_config.py",),
    "report.py": ("test_report.py",),
    "cli.py": ("test_cli.py",),
    "pipeline.py": ("test_cli.py",),
}

#: The faults injected. Each is a pattern and what it becomes -- all of them the kind
#: of thing a careless edit does: an inequality that lets one more case through, a
#: bound that is one out, a check that is skipped.
RULES: tuple[tuple[str, str, str], ...] = (
    (r"(?<![<>=!])>=(?!=)", "> ", "a bound loosened by one"),
    (r"(?<![<>=!])<=(?!=)", "< ", "a bound loosened by one"),
    (r"(?<![<>=!+\-*/])\bmin\(", "max(", "the wrong end of a range"),
    (r"(?<![<>=!+\-*/])\bmax\(", "min(", "the wrong end of a range"),
    (r"\bnot\s+", "", "a negation dropped"),
    (r"\band\b", "or", "a condition weakened"),
    (r"\ball\(", "any(", "every becomes at least one"),
    (r"\.x0\b", ".x1", "one edge of a box for another"),
    (r"\.y0\b", ".y1", "one edge of a box for another"),
    (r"\[0\]", "[1]", "the wrong element"),
    (r"\[-1\]", "[0]", "the wrong element"),
)

SKIP = ("import ", "from ", "assert ", "raise ")


@dataclass
class Mutant:
    module: str
    line: int
    before: str
    after: str
    kind: str
    killed: bool | None = None
    seconds: float = 0.0


@dataclass
class Result:
    mutants: list[Mutant] = field(default_factory=list)

    @property
    def killed(self) -> int:
        return sum(1 for m in self.mutants if m.killed)

    @property
    def survived(self) -> list[Mutant]:
        return [m for m in self.mutants if m.killed is False]


def prose(path: Path) -> dict[int, list[tuple[int, int]]]:
    """Which stretch of each line is a string or a comment.

    Changing a word inside a docstring changes nothing, so a mutation there survives
    every test and reads as a gap in the suite when it is a gap in this tool. Only
    the code on a line is worth mutating, and tokenising is what tells them apart.
    """
    import io
    import tokenize

    prose_types = {tokenize.STRING, tokenize.COMMENT}
    start_type = getattr(tokenize, "FSTRING_START", None)
    end_type = getattr(tokenize, "FSTRING_END", None)

    spans: dict[int, list[tuple[int, int]]] = {}

    def cover(begin, finish) -> None:
        (row0, col0), (row1, col1) = begin, finish
        for row in range(row0, row1 + 1):
            spans.setdefault(row, []).append((col0 if row == row0 else 0,
                                              col1 if row == row1 else 10_000))

    # An f-string is several tokens on this version of Python, and all of it counts
    # as prose -- including what is inside the braces, which is there to be written
    # into a message. A wrong column name in a sentence about a failure is a worse
    # message, not a worse program, and counting it as a fault the tests missed
    # would say the suite is weaker than it is.
    opened = None
    with path.open("rb") as handle:
        for token in tokenize.tokenize(io.BufferedReader(handle).readline):
            if start_type is not None and token.type == start_type and opened is None:
                opened = token.start
            elif end_type is not None and token.type == end_type and opened is not None:
                cover(opened, token.end)
                opened = None
            elif token.type in prose_types:
                cover(token.start, token.end)
    return spans


def candidates(path: Path) -> list[tuple[int, str, str, str]]:
    """Every fault this file admits: line number, the line, the mutated line, why."""
    spans = prose(path)
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        body = line.strip()
        if not body or body.startswith(SKIP):
            continue
        for pattern, replacement, kind in RULES:
            match = re.search(pattern, line)
            if match is None:
                continue
            if any(start <= match.start() < end for start, end in spans.get(i, ())):
                continue
            mutated = line[:match.start()] + replacement + line[match.end():]
            out.append((i, line, mutated, kind))
    return out


def prepare(work: Path) -> Path:
    """A throwaway copy of what a test run needs. Returns its source directory."""
    import shutil

    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for item in NEEDED:
        source = ROOT / item
        target = work / item
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, target)
    return work / "src" / "chartgen"


def baseline(work: Path) -> None:
    """Run the suite once, unmutated, and stop if anything is already failing.

    A copied tree that cannot import something fails every test, which makes every
    mutant look caught: the number would come out at a hundred percent and mean
    nothing at all.
    """
    every = sorted({name for tests in COVERED_BY.values() for name in tests})
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header",
                           "-p", "no:cacheprovider", "-x",
                           *[str(work / "tests" / "unit" / name) for name in every]],
                          cwd=work, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit("the copied tree does not pass its own tests, so nothing can "
                         "be learned from mutating it:\n" + done.stdout[-2000:])


def run_tests(work: Path, tests: tuple[str, ...]) -> bool:
    """True when every test passed. `-x` because one failure is the whole answer."""
    paths = [str(work / "tests" / "unit" / t) for t in tests]
    done = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "--no-header",
                           "-p", "no:cacheprovider", *paths],
                          cwd=work, capture_output=True, text=True)
    return done.returncode == 0


def check(src: Path, module: str, limit: int, rng: random.Random) -> list[Mutant]:
    path = src / module
    tests = COVERED_BY[module]
    picks = candidates(path)
    rng.shuffle(picks)
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    out: list[Mutant] = []
    try:
        for number, before, after, kind in picks[:limit]:
            mutant = Mutant(module, number, before.strip(), after.strip(), kind)
            ending = "\n" if lines[number - 1].endswith("\n") else ""
            lines[number - 1] = after + ending
            path.write_text("".join(lines), encoding="utf-8")
            started = time.time()
            try:
                mutant.killed = not run_tests(src.parents[1], tests)
            finally:
                lines[number - 1] = before + ending
                path.write_text("".join(lines), encoding="utf-8")
            mutant.seconds = round(time.time() - started, 1)
            out.append(mutant)
            print(f"  {'killed ' if mutant.killed else 'SURVIVED'} "
                  f"{module}:{number}  {kind}  ({mutant.seconds}s)", flush=True)
    finally:
        path.write_text(original, encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", action="append", help="restrict to these files")
    parser.add_argument("--limit", type=int, default=3, help="mutants per file")
    parser.add_argument("--seed", type=int, default=20260822)
    parser.add_argument("-o", "--out", default="review/data/mutation.json")
    parser.add_argument("--work", default="", help="scratch directory for the copy")
    args = parser.parse_args()

    import tempfile

    modules = args.module or list(COVERED_BY)
    rng = random.Random(args.seed)
    src = prepare(Path(args.work or (Path(tempfile.gettempdir()) / "chartgen-mutation")))
    print("checking the copy passes its own tests first", flush=True)
    baseline(src.parents[1])
    result = Result()
    for module in modules:
        print(module, flush=True)
        result.mutants += check(src, module, args.limit, rng)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"killed": result.killed, "total": len(result.mutants),
         "mutants": [vars(m) for m in result.mutants]},
        indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n{result.killed}/{len(result.mutants)} faults caught; "
          f"{len(result.survived)} survived -> {out}")


if __name__ == "__main__":
    main()
