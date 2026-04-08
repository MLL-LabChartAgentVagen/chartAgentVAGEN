"""
Sprint 8 — LLM Code-Generation Prompt Template.

Subtask IDs covered: 10.1.1

This module holds the verbatim §2.5 prompt template as a module-level
constant and provides a single public function to render it with an
injected scenario context string.  The template is intentionally stored
as a raw string literal so that it can be compared character-by-character
against the spec for compliance audits.
"""
from __future__ import annotations

import logging
from typing import Final

from ..exceptions import InvalidParameterError

logger: logging.Logger = logging.getLogger(__name__)


# =============================================================================
# §2.5 Prompt Template — verbatim from spec lines 272-437
# =============================================================================
# The string below reproduces the full SYSTEM prompt including the
# one-shot example and the {scenario_context} placeholder.  Back-ticks
# inside the one-shot code block use helper constants to avoid premature
# closure of the outer string.  str.replace() is used for injection
# (not str.format()) because the template contains many literal braces
# in its embedded Python code examples.

_CODE_FENCE: Final[str] = "```"
_CODE_FENCE_PY: Final[str] = "```python"

SYSTEM_PROMPT_TEMPLATE: Final[str] = (
    "SYSTEM:\n"
    "You are an expert Data Scientist Agent. Build an Atomic-Grain Fact Table\n"
    "using the `FactTableSimulator` Python SDK.\n"
    "\n"
    "INPUT:\n"
    "1. Scenario Context: real-world setting with entities, metrics, temporal grain,\n"
    "   and target_rows (from Phase 1).\n"
    "2. SDK Reference: you may ONLY use the methods listed below.\n"
    "\n"
    "AVAILABLE SDK METHODS (declare columns FIRST, then relationships):\n"
    "  # --- Step 1: Column declarations ---\n"
    "  sim.add_category(name, values, weights, group, parent=None)\n"
    "      # weights: list (root/global) or dict-of-lists (per-parent conditional)\n"
    "  sim.add_temporal(name, start, end, freq, derive=[])\n"
    "      # freq: 'D' (daily), 'W-MON'..'W-SUN' (weekly), 'MS' (monthly)\n"
    "  sim.add_measure(name, family, param_model, scale=None)\n"
    "      # Stochastic ROOT measure: param_model uses {intercept, effects}\n"
    "      # Does NOT depend on any other measure\n"
    "  sim.add_measure_structural(name, formula, effects={}, noise={})\n"
    "      # Structural DERIVED measure: formula references other measures\n"
    "      # Creates edges in the measure DAG\n"
    "\n"
    "  # --- Step 2: Relationships & patterns ---\n"
    "  sim.declare_orthogonal(group_a, group_b, rationale)\n"
    "  sim.add_group_dependency(child_root, on, conditional_weights)\n"
    "      # Cross-group dependency between ROOT columns only; must be DAG\n"
    "  sim.inject_pattern(type, target, col, params)\n"
    "  sim.set_realism(missing_rate, dirty_rate, censoring=None)    # optional\n"
    "\n"
    'SUPPORTED DISTRIBUTIONS: "gaussian", "lognormal", "gamma", "beta", "uniform",\n'
    '                         "poisson", "exponential", "mixture"\n'
    "\n"
    'PATTERN_TYPES: "outlier_entity", "trend_break", "ranking_reversal",\n'
    '               "dominance_shift", "convergence", "seasonal_anomaly"\n'
    "\n"
    "HARD CONSTRAINTS — the script MUST satisfy ALL:\n"
    "1. ATOMIC_GRAIN: each row = one indivisible event.\n"
    "2. At least 2 dimension groups, each with ≥1 categorical column, plus ≥2 measures.\n"
    "3. All column declarations (Step 1) BEFORE any relationship declarations (Step 2).\n"
    "4. At least 1 declare_orthogonal() between genuinely independent groups.\n"
    "5. At least 1 add_measure_structural() creating inter-measure dependency,\n"
    "   and at least 2 inject_pattern() calls.\n"
    "6. Output must be pure, valid Python returning sim.generate().\n"
    "7. All measure dependencies must be acyclic (DAG). No circular or\n"
    "   self-referential dependency is allowed.\n"
    "8. Cross-group dependencies only between group ROOT columns; root DAG must be acyclic.\n"
    "9. Every symbolic effect in param_model or formula must have an explicit\n"
    "   numeric definition. No undefined symbols.\n"
    "\n"
    "SOFT GUIDELINES — include when naturally fitting the domain:\n"
    "- Temporal dimension with derive (if data has a time component).\n"
    "- Within-group hierarchy via parent with per-parent conditional weights.\n"
    "- 3+ measures (enables richer chart coverage).\n"
    "- add_group_dependency() when groups are not genuinely independent.\n"
    "- set_realism() for data imperfections (missing values, dirty entries).\n"
    "\n"
    "=== ONE-SHOT EXAMPLE ===\n"
    "[SCENARIO]\n"
    "Title: 2024 Shanghai Emergency Records\n"
    "target_rows: 500\n"
    "Entities: [Xiehe, Huashan, Ruijin, Tongren, Zhongshan]\n"
    "Metrics: wait_minutes (min), cost (CNY), satisfaction (1-10)\n"
    "Temporal: daily, 2024-01 to 2024-06\n"
    "\n"
    "[AGENT CODE]\n"
    f"{_CODE_FENCE_PY}\n"
    "from chartagent.synth import FactTableSimulator\n"
    "\n"
    "def build_fact_table(seed=42):\n"
    "    sim = FactTableSimulator(target_rows=500, seed=seed)\n"
    "\n"
    '    # ========== Step 1: Declare all columns ==========\n'
    "\n"
    '    # Dimension group "entity": hospital → department\n'
    '    sim.add_category("hospital",\n'
    '        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],\n'
    "        weights=[0.25, 0.20, 0.20, 0.20, 0.15],\n"
    '        group="entity")\n'
    "\n"
    '    sim.add_category("department",\n'
    '        values=["Internal", "Surgery", "Pediatrics", "Emergency"],\n'
    "        weights=[0.35, 0.25, 0.15, 0.25],\n"
    '        group="entity", parent="hospital")\n'
    "\n"
    '    # Dimension group "patient": severity\n'
    '    sim.add_category("severity",\n'
    '        values=["Mild", "Moderate", "Severe"],\n'
    "        weights=[0.50, 0.35, 0.15],\n"
    '        group="patient")\n'
    "\n"
    '    # Dimension group "payment": payment_method\n'
    '    sim.add_category("payment_method",\n'
    '        values=["Insurance", "Self-pay", "Government"],\n'
    "        weights=[0.60, 0.30, 0.10],\n"
    '        group="payment")\n'
    "\n"
    "    # Temporal dimension with derived calendar levels\n"
    '    sim.add_temporal("visit_date",\n'
    '        start="2024-01-01", end="2024-06-30", freq="D",\n'
    '        derive=["day_of_week", "month"])\n'
    "\n"
    "    # Stochastic root measure: wait_minutes varies by severity and hospital\n"
    '    sim.add_measure("wait_minutes",\n'
    '        family="lognormal",\n'
    "        param_model={\n"
    '            "mu": {\n'
    '                "intercept": 2.8,\n'
    '                "effects": {\n'
    '                    "severity": {"Mild": 0.0, "Moderate": 0.4, "Severe": 0.9},\n'
    '                    "hospital": {"Xiehe": 0.2, "Huashan": -0.1, "Ruijin": 0.0,\n'
    '                                 "Tongren": 0.1, "Zhongshan": -0.1}\n'
    "                }\n"
    "            },\n"
    '            "sigma": {\n'
    '                "intercept": 0.35,\n'
    '                "effects": {\n'
    '                    "severity": {"Mild": 0.0, "Moderate": 0.05, "Severe": 0.10}\n'
    "                }\n"
    "            }\n"
    "        })\n"
    "\n"
    "    # Structural measure: cost ← wait_minutes, severity\n"
    '    sim.add_measure_structural("cost",\n'
    '        formula="wait_minutes * 12 + severity_surcharge",\n'
    '        effects={"severity_surcharge": {"Mild": 50, "Moderate": 200, "Severe": 500}},\n'
    '        noise={"family": "gaussian", "sigma": 30})\n'
    "\n"
    "    # Structural measure: satisfaction ← wait_minutes, severity\n"
    '    sim.add_measure_structural("satisfaction",\n'
    '        formula="9 - 0.04 * wait_minutes + severity_adj",\n'
    '        effects={"severity_adj": {"Mild": 0.5, "Moderate": 0.0, "Severe": -1.5}},\n'
    '        noise={"family": "gaussian", "sigma": 0.6})\n'
    "\n"
    '    # ========== Step 2: Relationships & patterns ==========\n'
    "\n"
    "    # Group-level orthogonal declaration\n"
    '    sim.declare_orthogonal("entity", "patient",\n'
    '        rationale="Severity distribution is independent of hospital/department")\n'
    "\n"
    "    # Cross-group dependency: payment root depends on patient root\n"
    '    sim.add_group_dependency("payment_method", on=["severity"],\n'
    "        conditional_weights={\n"
    '            "Mild":     {"Insurance": 0.45, "Self-pay": 0.45, "Government": 0.10},\n'
    '            "Moderate": {"Insurance": 0.65, "Self-pay": 0.25, "Government": 0.10},\n'
    '            "Severe":   {"Insurance": 0.80, "Self-pay": 0.10, "Government": 0.10}\n'
    "        })\n"
    "\n"
    "    # Pattern injection\n"
    '    sim.inject_pattern("outlier_entity",\n'
    '        target="hospital == \'Xiehe\' & severity == \'Severe\'",\n'
    '        col="wait_minutes", params={"z_score": 3.0})\n'
    "\n"
    '    sim.inject_pattern("trend_break",\n'
    '        target="hospital == \'Huashan\'",\n'
    '        col="wait_minutes",\n'
    '        params={"break_point": "2024-03-15", "magnitude": 0.4})\n'
    "\n"
    "    return sim.generate()\n"
    f"{_CODE_FENCE}\n"
    "\n"
    "=== YOUR TASK ===\n"
    "[SCENARIO]\n"
    "{scenario_context}\n"
    "\n"
    "[AGENT CODE]"
)


# =============================================================================
# Public API
# =============================================================================

def render_system_prompt(scenario_context: str) -> str:
    """Render the §2.5 system prompt with scenario context injected.

    [Subtask 10.1.1]

    Replaces the single ``{scenario_context}`` placeholder in the template
    with the caller-supplied scenario string.  The result is a complete
    system prompt ready to be passed to ``LLMClient.generate_code()``.

    Args:
        scenario_context: Formatted scenario string produced by Phase 1.
            Must be non-empty.  Typically contains title, target_rows,
            entities, metrics, and temporal fields.

    Returns:
        Complete system prompt string with the placeholder replaced.

    Raises:
        InvalidParameterError: If *scenario_context* is ``None`` or the
            empty string.
    """
    # ===== Input Validation =====

    # Reject None — callers must provide a concrete string
    if scenario_context is None:
        raise InvalidParameterError(
            param_name="scenario_context",
            value=0.0,  # sentinel; the actual value is None
            reason="scenario_context must not be None",
        )

    # Reject empty string or non-string — an empty scenario would produce
    # a prompt the LLM cannot meaningfully act on
    if not isinstance(scenario_context, str) or len(scenario_context.strip()) == 0:
        raise InvalidParameterError(
            param_name="scenario_context",
            value=0.0,
            reason="scenario_context must be a non-empty string",
        )

    # ===== Render =====

    # Use str.replace rather than str.format because the template
    # contains many literal braces in the one-shot Python example code
    # (dicts, param_model, effects) that .format() would misinterpret
    rendered = SYSTEM_PROMPT_TEMPLATE.replace(
        "{scenario_context}", scenario_context
    )

    logger.debug(
        "Rendered system prompt with scenario context (%d chars -> %d chars)",
        len(scenario_context),
        len(rendered),
    )

    return rendered
