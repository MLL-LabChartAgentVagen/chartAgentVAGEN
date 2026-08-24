"""The worked example, generated once per test session.

Every stage downstream of the data stage is exercised on the same emergency
department scenario the specification documents use, so a number that appears in
a test is a number that appears in the docs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chartgen.config import Config
from chartgen.s01_data.author import compose

SAMPLES = Path(__file__).resolve().parent / "samples"
SEED = 20260816


@pytest.fixture(autouse=True)
def no_model_calls(monkeypatch):
    """No test reaches a model.

    The suite covers the rules, and the rules are all of the pipeline but two calls.
    A test that sent a request would be slow, would cost money, and would stop being
    a test of anything reproducible. The text those calls write has a template
    fallback, which is what the suite exercises instead.
    """
    from chartgen.s02_figure import title

    monkeypatch.setattr(title, "default_llm", lambda config: None)


@pytest.fixture(scope="session")
def er_payload() -> dict:
    """The hand-written answer for the data stage: no model is called."""
    return json.loads((SAMPLES / "er_scenario.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def er(er_payload):
    """The 900-row fact table and its schema."""
    return compose(er_payload, scenario_id="er_wait", seed=SEED, config=Config.load())


@pytest.fixture(scope="session")
def logistics():
    """A second hand-written scenario, the one with a hierarchy: a site reports to
    exactly one region, which is what a colour group is allowed to carry."""
    payload = json.loads((SAMPLES / "logistics_scenario.json").read_text(encoding="utf-8"))
    return compose(payload, scenario_id="logistics", seed=SEED, config=Config.load())


@pytest.fixture(scope="session")
def er_table(er):
    return er[0]


@pytest.fixture(scope="session")
def er_schema(er):
    return er[1]
