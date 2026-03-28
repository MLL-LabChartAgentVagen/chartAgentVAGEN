# AGPDS — Sprint 2 Test Suite

## Project layout

```
agpds/
├── __init__.py          # Package exports (Sprint 1)
├── exceptions.py        # Exception hierarchy (Sprint 1)
├── models.py            # DimensionGroup, OrthogonalPair, GroupDependency (Sprint 1)
└── simulator.py         # FactTableSimulator with add_category + add_temporal (Sprint 2)
tests/
├── __init__.py
└── test_simulator_sprint2.py   # 176 tests covering Sprint 2
pyproject.toml
```

## Setup (one time)

```bash
cd <this-directory>
pip install -e ".[test]"
```

The `-e` flag installs the `agpds` package in editable mode so `import agpds` resolves
to the source files in this directory. The `[test]` extra pulls in `pytest`.

## Run the tests

```bash
# All 176 tests, verbose output
pytest -v

# Just the contract tests (rows 1–50)
pytest -v -k "TestContract"

# Just the integration tests
pytest -v -k "TestSprint1Sprint2"

# Single test by name
pytest -v -k "test_row04_per_parent_dict_valid"

# Stop on first failure
pytest -x

# With short traceback
pytest --tb=short
```

## Requirements

- Python 3.11+
- pytest >= 7.0 (installed by `pip install -e ".[test]"`)
- No other dependencies — the SDK uses only stdlib
