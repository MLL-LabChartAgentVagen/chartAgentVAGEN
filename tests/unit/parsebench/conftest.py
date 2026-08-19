"""Shared setup for the ParseBench page-analysis tests.

The analysis modules are scripts, not an installed package: each one is run
directly and imports its siblings by name. Putting their directory on the path
here is what lets the tests import them the same way.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "parsebench" / "tools" / "analysis"))


def component(key: str, figure_id: str = "f1", evidence: str = "the words on the page"):
    """A reported component. Every one carries evidence, so the tests build them so."""
    return {"key": key, "figure_id": figure_id, "evidence": evidence}


@pytest.fixture
def heading():
    """A figure's heading, split the five ways the schema asks for."""
    def make(**kw) -> dict:
        base = {"figure_number": "Figure 1", "title": "Waits", "subtitle": "",
                "unit_text": "", "placement": "above"}
        return {**base, **kw}
    return make


@pytest.fixture
def figure(heading):
    """One figure as the model reports it. Override any field per test."""
    def make(**kw) -> dict:
        base = {"id": "f1", "heading": heading(), "type": "bar", "type_other": "",
                "orientation": "vertical", "panels": 1, "panel_names": [], "series": 1,
                "series_names": [], "categories": 3, "category_names": [], "marks": 3,
                "values_printed": "none", "value_axis_ticks": "0, 20, 40",
                "source_line": ""}
        return {**base, **kw}
    return make


@pytest.fixture
def analysis(figure):
    """One page's structured answer."""
    def make(**kw) -> dict:
        base = {"page_note": "一页", "figures": [figure()],
                "components": [component("grouped_bar")], "new_components": [],
                "spot_checks": [], "hardest_step": 2, "difficulty_notes": "读不准",
                "unreadable": [], "suggestions": []}
        if "components" in kw:
            kw["components"] = [component(c) if isinstance(c, str) else c
                                for c in kw["components"]]
        return {**base, **kw}
    return make


@pytest.fixture
def result(analysis):
    """One page's answer plus the rules and findings that travel with it."""
    from checks import PageResult

    def make(**kw) -> "PageResult":
        base = {"stem": "doc_p1", "document": "doc", "tags": "need_estimate",
                "analysis": analysis(), "rules": [], "attribution": [], "findings": []}
        return PageResult(**{**base, **kw})
    return make
