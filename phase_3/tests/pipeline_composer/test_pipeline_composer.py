"""Test pipeline composition — sequential, forked, and nested shapes.

Loads master_data_3.csv + schema_metadata_3.json, picks a bar_chart view
via ViewEnumerator, and exercises all three pipeline shapes end-to-end,
including question generation via two-phase rendering.

Run:
    cd phase_3
    python -m tests.pipeline_composer.test_pipeline_composer
"""

import os
import sys
import json

# ── Path setup ────────────────────────────────────────────────────────────────
PHASE3_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PHASE3_DIR not in sys.path:
    sys.path.insert(0, PHASE3_DIR)

import pandas as pd

from view_enumerator import ViewEnumerator
from view_extractor import ViewData
from question_pipeline.pipeline_composer import PipelineComposer


# ── Fixtures ──────────────────────────────────────────────────────────────────

def load_data():
    """Load master_data_3.csv and schema_metadata_3.json."""
    data_dir = os.path.join(PHASE3_DIR, "example_data")
    master_df = pd.read_csv(os.path.join(data_dir, "master_data_3.csv"))
    with open(os.path.join(data_dir, "schema_metadata_3.json")) as f:
        schema = json.load(f)
    return master_df, schema


def pick_bar_view(master_df, schema):
    """Enumerate views and pick the highest-scoring bar_chart view."""
    enumerator = ViewEnumerator()
    views = enumerator.enumerate(schema, master_df)

    bar_views = [v for v in views if v.chart_type == "bar_chart"]
    if not bar_views:
        raise RuntimeError("No bar_chart views enumerated — check data/schema")

    # Pick the best-scoring bar view
    best = max(bar_views, key=lambda v: v.score)
    return best


# ── Test functions ────────────────────────────────────────────────────────────

def test_sequential(view_spec, view_df, composer):
    """Sequential: Filter(region == 'South') -> Sort(revenue, desc) -> Limit(3) -> Avg(revenue)."""
    print("=" * 60)
    print("TEST: Sequential Pipeline")
    print("=" * 60)

    pipe = composer.build_sequential(
        view_spec,
        filter_col="region",
        filter_op="==",
        filter_val="South",
        sort_col="revenue",
        sort_ascending=False,
        limit_k=3,
        measure_col="revenue",
    )

    print(f"\n{pipe.display()}")
    print(f"  type_check: {pipe.type_check()}")
    print(f"  op_count:   {pipe.op_count}")
    print(f"  depth:      {pipe.depth}")

    # Execute
    result = pipe.execute(view_df)
    print(f"  result:     {result}")
    assert result.is_scalar, f"Expected scalar, got {result.result_type}"
    print(f"  Answer:     {result.value:.2f}")

    # Question generation
    question = pipe.render_question(
        col="region", op="==", val="South",
        measure="revenue", direction="descending",
        k=3, entity_plural="regions",
    )
    print(f"  Question:   {question}")
    assert "{" not in question, f"Unfilled placeholder in question: {question}"
    print("  PASSED\n")
    return result


def test_forked(view_spec, view_df, composer):
    """Forked: Union(top-3 by revenue, bottom-2 by revenue) -> Count."""
    print("=" * 60)
    print("TEST: Forked (Parallel) Pipeline")
    print("=" * 60)

    pipe = composer.build_forked(
        view_spec,
        sort_col="revenue",
        limit_a=3,
        limit_b=2,
        measure_col="revenue",
    )

    print(f"\n{pipe.display()}")
    print(f"  type_check: {pipe.type_check()}")
    print(f"  op_count:   {pipe.op_count}")
    print(f"  depth:      {pipe.depth}")

    # Execute
    result = pipe.execute(view_df)
    print(f"  result:     {result}")
    assert result.is_scalar, f"Expected scalar, got {result.result_type}"
    print(f"  Answer:     {result.value}")

    # Question generation
    question = pipe.render_question(
        measure="revenue", direction="descending",
        k=3, entity_plural="regions",
    )
    print(f"  Question:   {question}")
    assert "{" not in question, f"Unfilled placeholder in question: {question}"
    print("  PASSED\n")
    return result


def test_nested(view_spec, view_df, composer):
    """Nested: Count where revenue > Avg(revenue)."""
    print("=" * 60)
    print("TEST: Nested Pipeline")
    print("=" * 60)

    # Build + realize
    pipe = composer.build_nested(
        view_spec,
        measure_col="revenue",
        filter_op=">",
    )
    realized = composer.realize_nested(pipe, view_df)

    print(f"\n{realized.display()}")
    print(f"  type_check: {realized.type_check()}")
    print(f"  op_count:   {realized.op_count}")
    print(f"  depth:      {realized.depth}")
    print(f"  threshold:  {realized._threshold:.2f} (inner Avg)")

    # Execute
    result = realized.execute(view_df)
    print(f"  result:     {result}")
    assert result.is_scalar, f"Expected scalar, got {result.result_type}"
    print(f"  Answer:     {result.value}")

    # Question generation
    question = realized.render_question(
        col="revenue", op=">", val=f"{realized._threshold:.2f}",
        entity_plural="regions",
    )
    print(f"  Question:   {question}")
    assert "{" not in question, f"Unfilled placeholder in question: {question}"
    print("  PASSED\n")
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading master_data_3.csv + schema_metadata_3.json ...")
    master_df, schema = load_data()
    print(f"  rows: {len(master_df)}, cols: {list(master_df.columns)}\n")

    print("Enumerating views ...")
    view_spec = pick_bar_view(master_df, schema)
    print(f"  Picked: {view_spec.chart_type}, binding={view_spec.binding}, score={view_spec.score:.1f}")

    # Extract the view
    view_data = ViewData(view_spec, master_df)
    view_df = view_data.extracted_view
    print(f"  Extracted view shape: {view_df.shape}")
    print(f"  Columns: {list(view_df.columns)}")
    print(f"  Preview:\n{view_df.head(10).to_string(index=False)}\n")

    composer = PipelineComposer()

    # Run all three tests
    test_sequential(view_spec, view_df, composer)
    test_forked(view_spec, view_df, composer)
    test_nested(view_spec, view_df, composer)

    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
