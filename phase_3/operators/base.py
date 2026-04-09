"""Operator base class and OperatorResult container."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional

import pandas as pd


@dataclass
class OperatorResult:
    """Typed wrapper: holds either a View (DataFrame) or a Scalar (value)."""

    result_type: str  # "V" or "S"
    value: Any        # DataFrame if "V", scalar if "S"

    # ── convenience predicates ────────────────────────────────────────────
    @property
    def is_view(self) -> bool:
        return self.result_type == "V"

    @property
    def is_scalar(self) -> bool:
        return self.result_type == "S"

    def __repr__(self) -> str:
        if self.is_scalar:
            return f"OperatorResult(S={self.value!r})"
        return f"OperatorResult(V, {len(self.value)} rows)"


class Operator(ABC):
    """Abstract base for every operator in the algebra.

    Subclass hierarchy::

        Operator
        ├── SetOperator      (V → V)
        ├── ScalarOperator   (V → S)
        ├── ScalarCombinator (S, S → S)
        ├── ViewCombinator   (V, V → V)
        └── BridgeOperator   (mixed)
    """

    # ── class-level metadata (override in each concrete class) ────────────
    name: str = ""
    input_type: str = ""          # "V", "S", "(S,S)", "(V,V)", "(S,V)"
    output_type: str = ""         # "V" or "S"
    compatible_charts: List[str] = []
    question_templates: List[str] = []

    # ── core interface ────────────────────────────────────────────────────
    @abstractmethod
    def execute(self, *inputs: Any) -> OperatorResult:
        """Run the operator on concrete data and return a typed result."""

    def is_compatible(self, chart_type: str) -> bool:
        """Return True if this operator is valid for *chart_type*."""
        return chart_type in self.compatible_charts

    def render_question(self, **kwargs: Any) -> str:
        """Fill in the first question template with *kwargs*.

        The exact template language is intentionally loose for now;
        concrete operators will refine it.
        """
        if not self.question_templates:
            return ""
        template = self.question_templates[0]
        try:
            return template.format(**kwargs)
        except KeyError:
            return template  # return raw if placeholders missing

    # ── dunder helpers ────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.input_type} → {self.output_type})"
