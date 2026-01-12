"""Question generators for line chart QA creation."""

from __future__ import annotations

from typing import Dict
import sys
from pathlib import Path

try:
    from templates.question_generator import QuestionGenerator
except ImportError:  # pragma: no cover - fallback when executed standalone
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.question_generator import QuestionGenerator


class LineQuestionGenerator(QuestionGenerator):
    """Base helper that exposes line-chart specific phrasing metadata."""

    def __init__(self, chart_metadata: Dict, config: Dict = None, random_state: int = None):
        super().__init__(chart_metadata, config, random_state)
        self.line_category = chart_metadata.get(
            "line_category", {"singular": "series", "plural": "series"}
        )
        self.metric_label = chart_metadata.get("y_label", self.y_axis)
        self.category_singular = self.line_category.get("singular", "series")
        self.category_plural = self.line_category.get("plural", "series")
        self.x_labels = chart_metadata.get("x_labels", [])
        self.period_idx = self._resolve_period_idx()
        self.period_label = self._resolve_period_label()

    def _resolve_period_idx(self) -> int:
        if not self.x_labels:
            return 0
        idx = (self.config or {}).get("period_idx", len(self.x_labels) - 1)
        return max(0, min(idx, len(self.x_labels) - 1))

    def _resolve_period_label(self) -> str:
        if not self.x_labels:
            return ""
        return str(self.x_labels[self.period_idx])

    def _period_clause(self) -> str:
        return f" in {self.period_label}" if self.period_label else ""


class SumQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        return (
            f"total {self.metric_label}{self._period_clause()} for the selected {self.category_plural}"
        )


class MeanQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"average {self.metric_label}{self._period_clause()} for the selected {self.category_plural}",
            f"mean {self.metric_label}{self._period_clause()} for the selected {self.category_plural}",
        ]
        return self.random_state.choice(templates)


class MedianQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"median {self.metric_label}{self._period_clause()} for the selected {self.category_plural}",
            f"middle {self.metric_label}{self._period_clause()} for the selected {self.category_plural}",
        ]
        return self.random_state.choice(templates)


class CountQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        return f"number of {self.category_plural}{self._period_clause()}"


class MaxQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"highest {self.metric_label}{self._period_clause()}",
            f"maximum {self.metric_label}{self._period_clause()}",
        ]
        return self.random_state.choice(templates)


class MinQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"lowest {self.metric_label}{self._period_clause()}",
            f"minimum {self.metric_label}{self._period_clause()}",
        ]
        return self.random_state.choice(templates)


class DifferenceQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        return f"difference in {self.metric_label}{self._period_clause()}"


class ReadValueQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        return f"{self.metric_label}{self._period_clause()}"


class ThresholdQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        threshold = (self.config or {}).get("threshold")
        direction = (self.config or {}).get("direction", "above")
        threshold_str = f"{threshold:g}" if isinstance(threshold, (int, float)) else threshold
        if threshold_str is None:
            return f"{self.category_plural}{self._period_clause()} that meet the threshold condition"
        return (
            f"{self.category_plural}{self._period_clause()} with "
            f"{self.metric_label} {direction} {threshold_str}"
        )


class KthQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        k = max(1, (self.config or {}).get("k", 1))
        direction = (self.config or {}).get("direction", "highest")
        ordinal = self._ordinal_suffix(k)
        return (
            f"{ordinal} {direction} {self.metric_label}{self._period_clause()} "
            f"among {self.category_plural}"
        )

    @staticmethod
    def _ordinal_suffix(k: int) -> str:
        if 10 <= k % 100 <= 20:
            return f"{k}th"
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
        return f"{k}{suffix}"


class TopkQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        k = max(1, (self.config or {}).get("k", 1))
        direction = (self.config or {}).get("direction", "top")
        direction_word = "top" if direction == "top" else "bottom"
        return (
            f"{direction_word} {k} {self.category_plural}{self._period_clause()} "
            f"by {self.metric_label}"
        )


class TakeAllQuestionGenerator(LineQuestionGenerator):
    def generate_question(self) -> str:
        return f"all {self.category_plural}{self._period_clause()}"


__all__ = [
    "LineQuestionGenerator",
    "SumQuestionGenerator",
    "MeanQuestionGenerator",
    "MedianQuestionGenerator",
    "CountQuestionGenerator",
    "MaxQuestionGenerator",
    "MinQuestionGenerator",
    "DifferenceQuestionGenerator",
    "ReadValueQuestionGenerator",
    "ThresholdQuestionGenerator",
    "KthQuestionGenerator",
    "TopkQuestionGenerator",
    "TakeAllQuestionGenerator",
]


