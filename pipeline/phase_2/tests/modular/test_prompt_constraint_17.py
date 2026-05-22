"""Tests for Constraint 17 (seasonal amplitude alignment) in SYSTEM_PROMPT_TEMPLATE.

First prompt-content tests in this codebase; pattern: substring + structural
ordering assertions on the rendered prompt. See
docs/soft_failure_fix/mechanisms/MECHANISM_6_SEASONAL_AMPLITUDE_DEEP_DIVE.md
"""
from __future__ import annotations

from pipeline.phase_2.orchestration.prompt import render_system_prompt


class TestConstraint17Substring:
    def test_constraint_17_header_present(self):
        rendered = render_system_prompt("dummy scenario")
        assert "17. SEASONAL AMPLITUDE" in rendered

    def test_constraint_17_mentions_validator_formula(self):
        """LLM must see how z is computed so it can size magnitude correctly."""
        rendered = render_system_prompt("dummy scenario")
        assert "baseline_std" in rendered
        assert "baseline_mean" in rendered

    def test_constraint_17_mentions_trend_break_fallback(self):
        """High-CV measures should be steered to trend_break."""
        rendered = render_system_prompt("dummy scenario")
        c17_start = rendered.index("17. SEASONAL AMPLITUDE")
        c17_end = rendered.index("SOFT GUIDELINES", c17_start)
        c17_block = rendered[c17_start:c17_end]
        assert "trend_break" in c17_block

    def test_constraint_17_includes_numeric_example(self):
        """Match Constraint 13's precedent: include a worked numeric example."""
        rendered = render_system_prompt("dummy scenario")
        c17_start = rendered.index("17. SEASONAL AMPLITUDE")
        c17_end = rendered.index("SOFT GUIDELINES", c17_start)
        c17_block = rendered[c17_start:c17_end]
        assert "Example" in c17_block or "example" in c17_block


class TestConstraint17Placement:
    def test_constraint_17_in_hard_constraints_section(self):
        rendered = render_system_prompt("dummy scenario")
        hard_start = rendered.index("HARD CONSTRAINTS")
        soft_start = rendered.index("SOFT GUIDELINES")
        c17_idx = rendered.index("17. SEASONAL AMPLITUDE")
        assert hard_start < c17_idx < soft_start

    def test_constraint_17_appears_after_constraint_13(self):
        rendered = render_system_prompt("dummy scenario")
        c13_idx = rendered.index("13. KS-CELL DENSITY")
        c17_idx = rendered.index("17. SEASONAL AMPLITUDE")
        assert c13_idx < c17_idx

    def test_numbering_gap_14_15_16_intentional(self):
        """14/15/16 NOT present (reserved per PINGYUE §8.x for Phase A/B/C)."""
        rendered = render_system_prompt("dummy scenario")
        hard_start = rendered.index("HARD CONSTRAINTS")
        soft_start = rendered.index("SOFT GUIDELINES")
        block = rendered[hard_start:soft_start]
        for n in (14, 15, 16):
            assert f"\n{n}. " not in block, (
                f"Constraint {n} should be reserved for Phase A/B/C; "
                "current Phase D uses 17 to leave the gap"
            )


class TestConstraint17RowCountGuardrail:
    """Phase D.2: anomaly_window × target row-count guardrail sub-clause."""

    def _c17_block(self) -> str:
        rendered = render_system_prompt("dummy scenario")
        c17_start = rendered.index("17. SEASONAL AMPLITUDE")
        c17_end = rendered.index("SOFT GUIDELINES", c17_start)
        return rendered[c17_start:c17_end]

    def test_subclause_mentions_expected_rows_formula(self):
        block = self._c17_block()
        assert "expected_rows" in block

    def test_subclause_mentions_hard_floor_5_and_soft_floor_10(self):
        """Phase D.2 design: hard floor 5 (Poisson reliability), soft 10
        (z stability) — explicitly chosen over Constraint 13's KS ≥ 30."""
        block = self._c17_block()
        b = block.lower()
        # The sub-clause must label its two floors
        assert "hard floor" in b
        assert "soft floor" in b
        # The chosen thresholds must appear adjacent to expected_rows
        assert "expected_rows ≥ 5" in block or "expected_rows >= 5" in block
        assert "expected_rows ≥ 10" in block or "expected_rows >= 10" in block

    def test_subclause_advises_widen_or_drop_target(self):
        block = self._c17_block()
        b = block.lower()
        assert "widen" in b
        assert "remove" in b or "drop" in b or "broaden" in b

    def test_subclause_includes_e9c4_counter_example(self):
        """Worked numeric example matches the actual production failure
        (target_rows=420, temporal_range=290 days, weights[9]=0.095,
        anomaly_window=12 days, expected_rows≈1.6)."""
        block = self._c17_block()
        assert "420" in block
        assert "290" in block
        assert "1.6" in block or "12" in block

    def test_subclause_appears_after_trend_break_example(self):
        """Logical flow: amplitude/CV math → trend_break fallback → row
        guardrail. The guardrail limits the 'narrow window' advice given
        earlier; it must come after the magnitude/CV/trend_break section."""
        block = self._c17_block()
        trend_break_idx = block.index("trend_break")
        guardrail_idx = block.index("expected_rows")
        assert trend_break_idx < guardrail_idx, (
            "Row-count guardrail must follow the trend_break fallback "
            "(it limits the 'narrow window' advice given earlier)"
        )

    def test_no_new_constraint_18_introduced(self):
        """D.2 keeps the guardrail INSIDE Constraint 17 — must not
        accidentally introduce a 'Constraint 18' header."""
        rendered = render_system_prompt("dummy scenario")
        hard = rendered.index("HARD CONSTRAINTS")
        soft = rendered.index("SOFT GUIDELINES")
        block = rendered[hard:soft]
        assert "\n18. " not in block, (
            "Phase D.2 sub-clause must live inside Constraint 17; "
            "spawning Constraint 18 reflects an unintended scope leak."
        )
