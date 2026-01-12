"""Question generator classes for heatmap QA pairs."""

from __future__ import annotations

from typing import Dict
import sys
from pathlib import Path

try:
    from templates.question_generator import QuestionGenerator
except ImportError:  # pragma: no cover
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.question_generator import QuestionGenerator


class HeatmapQuestionGenerator(QuestionGenerator):
    """Base helper providing heatmap-specific phrasing details."""

    def __init__(self, chart_metadata: Dict, config: Dict = None, random_state: int = None):
        super().__init__(chart_metadata, config, random_state)
        category = chart_metadata.get("heatmap_category", {"singular": "value", "plural": "values"})
        self.metric_singular = category.get("singular", "value")
        self.metric_plural = category.get("plural", "values")


class SumQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return f"total {self.metric_plural} across the selected cells"


class MeanQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"average {self.metric_plural} across the selected cells",
            f"mean {self.metric_plural} across the selected cells",
        ]
        return self.random_state.choice(templates)


class MedianQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        templates = [
            f"median {self.metric_plural} across the selected cells",
            f"middle {self.metric_plural} across the selected cells",
        ]
        return self.random_state.choice(templates)


class CountQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return "number of heatmap cells selected"


class MaxQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return f"highest {self.metric_singular} among the selected cells"


class MinQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return f"lowest {self.metric_singular} among the selected cells"


class DifferenceQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return f"difference in {self.metric_plural} between the selected cells"


class ReadValueQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return f"{self.metric_plural} of the selected cells"


class ThresholdQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        threshold = (self.config or {}).get("threshold")
        direction = (self.config or {}).get("direction", "above")
        threshold_str = f"{threshold:g}" if isinstance(threshold, (int, float)) else threshold
        if threshold_str is None:
            return f"cells satisfying the threshold condition for {self.metric_plural}"
        return f"cells with {self.metric_plural} {direction} {threshold_str}"


class KthQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        k = max(1, (self.config or {}).get("k", 1))
        direction = (self.config or {}).get("direction", "highest")
        ordinal = self._ordinal_suffix(k)
        return f"{ordinal} {direction} {self.metric_singular} among the selected cells"

    @staticmethod
    def _ordinal_suffix(k: int) -> str:
        if 10 <= k % 100 <= 20:
            return f"{k}th"
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
        return f"{k}{suffix}"


class TopkQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        k = max(1, (self.config or {}).get("k", 1))
        direction = (self.config or {}).get("direction", "top")
        direction_word = "top" if direction == "top" else "bottom"
        return f"{direction_word} {k} cells by {self.metric_singular}"


class TakeAllQuestionGenerator(HeatmapQuestionGenerator):
    def generate_question(self) -> str:
        return "all heatmap cells"


__all__ = [
    "HeatmapQuestionGenerator",
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


