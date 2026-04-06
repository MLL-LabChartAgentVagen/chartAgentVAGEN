"""Root test runner with clean console output.

Warnings are captured per test-class suite and displayed as a deduplicated
block below each suite's results, not inline.

Run from phase_3/ or from tests/:
    python tests/run_all.py
    python run_all.py
"""
import io
import os
import sys
import time
import unittest
import warnings as _warnings

# ── Path setup ───────────────────────────────────────────────────────────────
TESTS_DIR  = os.path.dirname(os.path.abspath(__file__))
PHASE3_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
if PHASE3_DIR not in sys.path:
    sys.path.insert(0, PHASE3_DIR)

# ── ANSI colours (auto-disabled when not a TTY) ───────────────────────────────
_TTY = sys.stdout.isatty()

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if _TTY else text

GREEN  = lambda t: _c("32", t)
RED    = lambda t: _c("31", t)
YELLOW = lambda t: _c("33", t)
CYAN   = lambda t: _c("36", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)

PASS_MARK = GREEN("  PASS")
FAIL_MARK = RED("  FAIL")
SKIP_MARK = YELLOW("  SKIP")

WIDTH = 52


# ── Helpers ───────────────────────────────────────────────────────────────────
def _flatten(suite):
    """Yield individual TestCase instances from a nested suite tree."""
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _flatten(item)
        else:
            yield item


def _suite_folder(test) -> str:
    """Return the folder name component, e.g. 'dashboard_composer'."""
    parts = test.__class__.__module__.split(".")
    return parts[-2] if len(parts) >= 2 else parts[0]


def _group_by_folder(suite) -> dict:
    """Order-preserving dict: folder -> list[TestCase]."""
    groups: dict[str, list] = {}
    for t in _flatten(suite):
        groups.setdefault(_suite_folder(t), []).append(t)
    return groups


def _rebuild_class_suites(tests: list) -> unittest.TestSuite:
    """Reconstruct per-class sub-suites so setUpClass/tearDownClass fire."""
    by_class: dict = {}
    for t in tests:
        by_class.setdefault(t.__class__, []).append(t)
    top = unittest.TestSuite()
    for cls, cases in by_class.items():
        top.addTest(unittest.TestSuite(cases))
    return top


# ── Custom result (display only, no suite orchestration) ─────────────────────
class PrettyResult(unittest.TestResult):

    def addSuccess(self, test):
        super().addSuccess(test)
        name = test._testMethodName
        doc  = (test._testMethodDoc or "").strip().split("\n")[0]
        print(f"{PASS_MARK}  {name}")
        if doc:
            print(f"         {DIM(doc)}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"{FAIL_MARK}  {test._testMethodName}  {YELLOW('[error]')}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"{FAIL_MARK}  {test._testMethodName}  {YELLOW('[assertion]')}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        print(f"{SKIP_MARK}  {test._testMethodName}  {DIM(reason)}")


# ── Pretty runner ─────────────────────────────────────────────────────────────
class PrettyRunner:
    def run(self, suite: unittest.TestSuite) -> PrettyResult:
        groups    = _group_by_folder(suite)
        n_tests   = sum(len(v) for v in groups.values())
        result    = PrettyResult()
        all_start = time.time()

        print()
        print(BOLD(f"  Running {n_tests} tests"))
        print(DIM(f"  {'=' * WIDTH}"))

        for folder, tests in groups.items():
            label = folder.replace("_", " ").title()
            print()
            print(f"  {BOLD(CYAN(label))}")
            print(DIM(f"  {'─' * WIDTH}"))

            n_before  = result.testsRun
            e_before  = len(result.errors) + len(result.failures)
            start     = time.time()

            # Run this folder's tests as proper class sub-suites
            # so setUpClass/tearDownClass are respected.
            # Capture warnings via the warnings module; suppress stderr noise.
            folder_suite = _rebuild_class_suites(tests)
            with _warnings.catch_warnings(record=True) as caught:
                _warnings.simplefilter("always")
                # Swallow stderr to prevent warnings that slip through printing
                old_stderr = sys.stderr
                sys.stderr = io.StringIO()
                try:
                    folder_suite.run(result)
                finally:
                    sys.stderr = old_stderr

            elapsed  = time.time() - start
            n_ran    = result.testsRun - n_before
            n_fail   = (len(result.errors) + len(result.failures)) - e_before
            status   = GREEN("all passed") if n_fail == 0 else RED(f"{n_fail} failed")

            # Deduplicate and display captured warnings
            seen_msgs: list[str] = []
            for w in caught:
                # Just show the first line of the message
                msg = f"{w.category.__name__}: {str(w.message).split(chr(10))[0]}"
                if msg not in seen_msgs:
                    seen_msgs.append(msg)

            if seen_msgs:
                print(DIM(f"  {'·' * WIDTH}"))
                count_label = "1 warning" if len(seen_msgs) == 1 \
                              else f"{len(seen_msgs)} warnings"
                print(f"  {YELLOW(count_label)}")
                for msg in seen_msgs:
                    short = msg if len(msg) <= 70 else msg[:67] + "..."
                    print(f"    {DIM(short)}")

            print(DIM(f"  {'─' * WIDTH}"))
            print(f"  {status}  "
                  f"{DIM(f'{n_ran - n_fail}/{n_ran}')}  "
                  f"{DIM(f'{elapsed * 1000:.0f} ms')}")

        # ── Final summary ─────────────────────────────────────────────────────
        elapsed = time.time() - all_start
        n_fail  = len(result.errors) + len(result.failures)
        n_pass  = n_tests - n_fail

        print()
        print(DIM(f"  {'=' * WIDTH}"))
        if n_fail == 0:
            print(f"  {BOLD(GREEN('OK'))}  "
                  f"{DIM(f'{n_pass}/{n_tests} passed  —  {elapsed * 1000:.0f} ms total')}")
        else:
            print(f"  {BOLD(RED('FAILED'))}  "
                  f"{DIM(f'{n_pass}/{n_tests} passed  {n_fail} failed  —  {elapsed * 1000:.0f} ms total')}")
        print()

        # ── Error / failure details ───────────────────────────────────────────
        for label, items in (("ERROR", result.errors), ("FAIL", result.failures)):
            for test, tb in items:
                print(f"  {RED(BOLD(label))}: {test}")
                for line in tb.strip().split("\n")[-5:]:
                    print(f"    {DIM(line)}")
                print()

        return result


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = lambda a, b: (a > b) - (a < b)

    suite = loader.discover(
        start_dir=TESTS_DIR,
        pattern="test_*.py",
        top_level_dir=PHASE3_DIR,
    )

    result = PrettyRunner().run(suite)
    sys.exit(0 if not result.errors and not result.failures else 1)
