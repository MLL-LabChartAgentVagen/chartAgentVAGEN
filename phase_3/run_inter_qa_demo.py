"""
Demo: Dashboard composition + inter-chart QA generation
========================================================
Run from the phase_3/ directory:

    python run_inter_qa_demo.py

What it does
------------
1. Builds a realistic master DataFrame (sales by region, segment, and month).
2. Enumerates feasible ViewSpecs from the schema metadata.
3. Composes dashboards for k=2, k=3, and k=4.
4. Generates all inter-view QA pairs for each dashboard.
5. Prints a nicely formatted summary to the terminal.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd

from view_spec import ViewSpec
from view_extractor import ViewData
from view_enumerator import ViewEnumerator
from dashboard_composer import DashboardComposer
from dashboard import Dashboard
from interQAGenerator.inter_qa_generator import InterQAGenerator

# ── Colour helpers (graceful fallback if terminal has no colour) ──────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
DIM    = "\033[2m"

def _h1(text: str) -> str:
    bar = "═" * (len(text) + 4)
    return f"\n{BOLD}{CYAN}╔{bar}╗\n║  {text}  ║\n╚{bar}╝{RESET}"

def _h2(text: str) -> str:
    return f"\n{BOLD}{YELLOW}▸ {text}{RESET}"

def _h3(text: str) -> str:
    return f"  {BOLD}{GREEN}◆ {text}{RESET}"

def _kv(key: str, value: str) -> str:
    return f"    {DIM}{key}:{RESET} {value}"

def _qa_block(qa: dict, idx: int) -> str:
    difficulty_color = {
        "easy": GREEN, "medium": YELLOW,
        "hard": MAGENTA, "very_hard": "\033[31m",  # red
    }.get(qa.get("difficulty", ""), DIM)
    diff_label = f"{difficulty_color}[{qa.get('difficulty','?')}]{RESET}"
    lines = [
        f"    {BOLD}Q{idx}:{RESET} {qa['question']}",
        f"       {GREEN}→{RESET} {qa['answer']}",
        f"       {DIM}template: {qa['template']}  {diff_label}{RESET}",
    ]
    return "\n".join(lines)


# ── 1. Master dataset ─────────────────────────────────────────────────────────

SCHEMA = {
    "columns": [
        {"name": "region",   "type": "categorical", "role": "primary",     "group": "geo"},
        {"name": "segment",  "type": "categorical", "role": "secondary",   "group": "seg"},
        {"name": "channel",  "type": "categorical", "role": "orthogonal",  "group": "ch"},
        {"name": "revenue",  "type": "measure"},
        {"name": "cost",     "type": "measure"},
        {"name": "units",    "type": "measure"},
        {"name": "date",     "type": "temporal"},
    ],
    "dimension_groups": {
        "geo": ["region"],
        "seg": ["segment"],
        "ch":  ["channel"],
    },
    "orthogonal_pairs": [
        {"col_a": "region",  "col_b": "segment"},
        {"col_a": "region",  "col_b": "channel"},
    ],
    # Keep empty to avoid the unimplemented _extract_formula_columns path
    # in DashboardComposer.  The causal_chain dashboard is hand-crafted below.
    "dependencies": [],
    "correlations": [],
    "patterns": [],
}

MASTER_DF = pd.DataFrame({
    "region":  ["North","South","East","West"] * 12,
    "segment": (["A","A","B","B"] * 6 + ["B","B","A","A"] * 6),
    "channel": (["Online"] * 24 + ["Retail"] * 24),
    "date":    pd.date_range("2023-01", periods=48, freq="ME"),
    "revenue": [
        120,230,180,310, 115,225,190,305, 125,240,175,320,
        130,235,185,315, 118,228,195,308, 122,232,178,322,
        140,260,195,340, 135,255,205,335, 145,265,190,345,
        138,258,200,338, 142,262,198,342, 136,256,202,336,
    ],
    "cost": [
        55,100,80,140, 52,98,85,137, 57,103,78,143,
        59,101,82,141, 54,99,87,139, 56,102,79,144,
        63,115,88,153, 61,112,92,150, 65,118,86,156,
        62,114,90,152, 64,116,89,154, 60,111,91,151,
    ],
    "units": [
        12,23,18,31, 11,22,19,30, 12,24,17,32,
        13,23,18,31, 11,22,19,30, 12,23,17,32,
        14,26,19,34, 13,25,20,33, 14,26,19,34,
        13,25,20,33, 14,26,19,34, 13,25,20,33,
    ],
})


# ── 2. Enumerate views ────────────────────────────────────────────────────────

def build_views(schema: dict, master: pd.DataFrame) -> list:
    enumerator = ViewEnumerator()
    views = enumerator.enumerate(schema, master)
    extracted = []
    for v in views:
        try:
            vd = ViewData(v, master)
            v.extracted_view = vd.extracted_view
            extracted.append(v)
        except Exception:
            pass
    return extracted


# ── 3. Main demo ──────────────────────────────────────────────────────────────

def run_demo():
    print(_h1("Dashboard + Inter-Chart QA  Demo"))

    # --- build views ---
    print(_h2("Step 1 — Enumerate views from master table"))
    views = build_views(SCHEMA, MASTER_DF)
    print(_kv("Master shape", f"{MASTER_DF.shape[0]} rows × {MASTER_DF.shape[1]} cols"))
    print(_kv("Feasible views enumerated", str(len(views))))

    # --- compose dashboards ---
    print(_h2("Step 2 — Compose dashboards"))
    composer = DashboardComposer()
    gen = InterQAGenerator()

    MAX_PER_K = 3  # cap per k-value to keep output readable

    all_dashboards: list[Dashboard] = []
    for k in (2, 3, 4):
        dashes = composer.compose(views, SCHEMA, target_k=k)
        # Sort by composite score (descending) and keep the top few
        dashes.sort(key=lambda d: d.score, reverse=True)
        sampled = dashes[:MAX_PER_K]
        print(_kv(f"k={k} dashboards (total / shown)", f"{len(dashes)} / {len(sampled)}"))
        all_dashboards.extend(sampled)

    # Always include hand-crafted dashboards to demonstrate every relationship type,
    # since the composer skips causal_chain/drill_down when the schema is minimal.
    crafted = _hand_crafted_dashboards(MASTER_DF)
    print(_kv("Hand-crafted dashboards (drill_down, dual_metric, causal_chain)",
              str(len(crafted))))
    all_dashboards.extend(crafted)

    if not all_dashboards:
        print("\n  No dashboards produced — check schema or master data.\n")
        return

    # --- generate & display QA for each dashboard ---
    print(_h2("Step 3 — Generate inter-chart QA"))

    shown = 0
    for dash in all_dashboards:
        qa_pairs = gen.generate_all_qa(dash)
        if not qa_pairs:
            continue

        # Write QA back onto the dashboard object
        for qa in qa_pairs:
            dash.add_qa(qa)

        shown += 1
        print()
        print(_h3(dash.title))
        print(_kv("Pattern",      dash.pattern))
        print(_kv("Relationship", dash.relationship))
        print(_kv("Layout",       dash.layout))
        print(_kv("Score",        f"{dash.score:.2f}"))
        print(_kv("Charts",       "  |  ".join(
            f"{v.chart_type} [{v.binding.get('measure') or v.binding.get('m1','')}]"
            for v in dash.views
        )))
        print()
        for i, qa in enumerate(qa_pairs, start=1):
            print(_qa_block(qa, i))
        print()
        print("  " + "─" * 70)

    # --- summary ---
    total_qa = sum(len(d.qa_pairs) for d in all_dashboards)
    print(_h2("Summary"))
    print(_kv("Dashboards composed",      str(len(all_dashboards))))
    print(_kv("Dashboards with QA",       str(shown)))
    print(_kv("Total inter-chart QA pairs", str(total_qa)))
    print()


def _hand_crafted_dashboards(master: pd.DataFrame) -> list[Dashboard]:
    """
    Fallback: manually build three realistic dashboards when the enumerator
    produces nothing (e.g. the schema doesn't match any extraction rule).
    """
    from view_extraction_rules import VIEW_EXTRACTION_RULES

    agg = master.groupby("region").agg(
        revenue=("revenue", "sum"), cost=("cost", "sum"), units=("units", "sum")
    ).reset_index()

    rule = VIEW_EXTRACTION_RULES.get("bar_chart", {})

    # --- dual_metric: revenue vs cost by region ---
    v_rev = ViewSpec("bar_chart", {"cat": "region", "measure": "revenue"}, rule, score=3.5)
    v_rev.extracted_view = agg[["region", "revenue"]]
    v_cost = ViewSpec("bar_chart", {"cat": "region", "measure": "cost"}, rule, score=3.2)
    v_cost.extracted_view = agg[["region", "cost"]]
    d1 = Dashboard(views=[v_rev, v_cost], relationship="dual_metric",
                   pattern="dual_metric")

    # --- drill_down: bar (overview) + grouped bar (by segment detail) ---
    agg_seg = master.groupby(["region", "segment"])["revenue"].sum().reset_index()
    r_detail = VIEW_EXTRACTION_RULES.get("grouped_bar_chart", rule)
    v_overview = ViewSpec("bar_chart", {"cat": "region", "measure": "revenue"}, rule, score=3.5)
    v_overview.extracted_view = agg[["region", "revenue"]]
    v_detail = ViewSpec("grouped_bar_chart",
                        {"cat": "region", "cat2": "segment", "measure": "revenue"},
                        r_detail, score=2.8)
    v_detail.extracted_view = agg_seg
    d2 = Dashboard(views=[v_overview, v_detail], relationship="drill_down",
                   pattern="overview_detail")

    # --- causal_chain: ad spend → units → revenue (time-series simulation) ---
    ts = master.groupby("date").agg(
        revenue=("revenue", "sum"), cost=("cost", "sum"), units=("units", "sum")
    ).reset_index()
    r_line = VIEW_EXTRACTION_RULES.get("line_chart", rule)
    v_cause = ViewSpec("line_chart", {"time": "date", "measure": "cost"}, r_line, score=2.0)
    v_cause.extracted_view = ts[["date", "cost"]]
    v_med = ViewSpec("line_chart", {"time": "date", "measure": "units"}, r_line, score=2.0)
    v_med.extracted_view = ts[["date", "units"]]
    v_effect = ViewSpec("line_chart", {"time": "date", "measure": "revenue"}, r_line, score=2.0)
    v_effect.extracted_view = ts[["date", "revenue"]]
    d3 = Dashboard(views=[v_cause, v_med, v_effect], relationship="causal_chain",
                   pattern="cause_mediator_effect")

    return [d1, d2, d3]


if __name__ == "__main__":
    run_demo()
