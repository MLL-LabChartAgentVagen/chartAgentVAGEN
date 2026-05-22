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
