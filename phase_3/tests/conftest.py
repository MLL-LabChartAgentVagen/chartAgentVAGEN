"""Shared fixtures for all test modules.

Import directly in test files — no pytest dependency.
All fixtures are plain functions/constants.
"""
import os
import sys
import pandas as pd

# ── Ensure phase_3/ is importable from any test sub-folder ──────────────────
PHASE3_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PHASE3_DIR not in sys.path:
    sys.path.insert(0, PHASE3_DIR)

from view_spec import ViewSpec
from view_extraction_rules import VIEW_EXTRACTION_RULES

# ── Mini schema_metadata ─────────────────────────────────────────────────────
MINI_SCHEMA = {
    "columns": [
        {"name": "region",   "type": "categorical", "role": "primary",  "group": "geo"},
        {"name": "segment",  "type": "categorical", "role": "secondary", "group": "seg"},
        {"name": "revenue",  "type": "measure"},
        {"name": "date",     "type": "temporal"},
    ],
    "dimension_groups": {"geo": ["region"], "seg": ["segment"]},
    "orthogonal_pairs": [{"col_a": "region", "col_b": "segment"}],
    "dependencies": [],
    "correlations": [],
    "patterns": [],
}

# ── Mini master DataFrame ────────────────────────────────────────────────────
MINI_DF = pd.DataFrame({
    "region":  ["North", "South", "East", "West", "North",
                "South", "East",  "West", "North", "South"],
    "segment": ["A", "A", "B", "B", "A", "B", "A", "B", "A", "B"],
    "revenue": [100, 200, 150, 300, 120, 180, 160, 250, 90, 210],
    "date":    pd.date_range("2023-01", periods=10, freq="ME"),
})

# ── Factory helpers ───────────────────────────────────────────────────────────

def make_bar_spec(extracted: bool = True) -> ViewSpec:
    """Return a bar_chart ViewSpec; optionally pre-populate extracted_view."""
    rule = VIEW_EXTRACTION_RULES["bar_chart"]
    spec = ViewSpec(
        chart_type="bar_chart",
        binding={"cat": "region", "measure": "revenue"},
        rule=rule,
        score=3.5,
    )
    if extracted:
        spec.extracted_view = (
            MINI_DF.groupby("region")["revenue"].mean().reset_index()
        )
    return spec


def make_line_spec(extracted: bool = True) -> ViewSpec:
    """Return a line_chart ViewSpec with a temporal binding."""
    rule = VIEW_EXTRACTION_RULES["line_chart"]
    spec = ViewSpec(
        chart_type="line_chart",
        binding={"time": "date", "series": "region", "measure": "revenue"},
        rule=rule,
        score=2.0,
    )
    if extracted:
        spec.extracted_view = (
            MINI_DF.groupby(["date", "region"])["revenue"].mean().reset_index()
        )
    return spec


def make_scatter_spec(extracted: bool = True) -> ViewSpec:
    """Return a scatter_plot ViewSpec with two measure bindings."""
    rule = VIEW_EXTRACTION_RULES["scatter_plot"]
    df = pd.DataFrame({
        "revenue": range(50, 100),
        "cost":    range(30, 80),
        "region":  (["North", "South"] * 25),
    })
    spec = ViewSpec(
        chart_type="scatter_plot",
        binding={"m1": "revenue", "m2": "cost", "color": "region"},
        rule=rule,
        score=1.5,
    )
    if extracted:
        spec.extracted_view = df
    return spec
