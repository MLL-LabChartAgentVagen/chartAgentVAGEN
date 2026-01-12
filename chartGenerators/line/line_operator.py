"""Operators specialized for line chart QA generation."""

from __future__ import annotations

from abc import abstractmethod
from typing import Dict, List
import sys
from pathlib import Path

try:
    from templates.operator import Operator, OperatorResult
except ImportError:  # pragma: no cover - fallback when running standalone
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.operator import Operator, OperatorResult


class LineOperator(Operator):
    """Base helper providing line-chart specific state."""

    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        super().__init__(chart_metadata, config, random_state)
        self.line_data = self.chart_metadata.get("line_data", [])
        self.line_labels = self.chart_metadata.get("line_labels", [])
        self.x_labels = self.chart_metadata.get("x_labels", [])
        self.line_category = self.chart_metadata.get(
            "line_category", {"singular": "series", "plural": "series"}
        )
        self.metric_label = self.chart_metadata.get("y_label", "value")
        self.period_idx = self._resolve_period_idx()
        self.period_label = self._resolve_period_label()
        self.line_values = self._compute_line_values()
        # Reuse base compatibility fields
        self.bar_data = self.line_values
        self.category_singular = self.line_category.get("singular", "series")
        self.category_plural = self.line_category.get("plural", "series")

    def _resolve_period_idx(self) -> int:
        if not self.x_labels:
            return 0
        idx = self.config.get("period_idx", len(self.x_labels) - 1)
        return max(0, min(idx, len(self.x_labels) - 1))

    def _resolve_period_label(self) -> str:
        if not self.x_labels:
            return ""
        return str(self.x_labels[self.period_idx])

    def _compute_line_values(self) -> List[float]:
        if not self.line_data:
            return []
        values = []
        for series in self.line_data:
            if self.period_idx < len(series):
                values.append(series[self.period_idx])
            else:
                # Fallback to last observed point if index is out of range
                values.append(series[-1])
        return values

    def _period_clause(self) -> str:
        return f" in {self.period_label}" if self.period_label else ""


class LineZeroStepOperator(LineOperator):
    """Abstract base class for zero-step operators."""

    @abstractmethod
    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        raise NotImplementedError


class LineOneStepOperator(LineOperator):
    """Abstract base class for one-step operators."""

    @abstractmethod
    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        raise NotImplementedError


class SumOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate total {metric}{period_clause} for the selected {category}.",
        "I will add up the {metric}{period_clause} for the selected {category}.",
        "I should compute the sum of {metric}{period_clause} for these {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        total = sum(self.line_values[i] for i in line_indices)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_plural,
            )
        ]
        return OperatorResult(total, line_indices, reasoning, [line_indices])


class MeanOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate average {metric}{period_clause} for the selected {category}.",
        "I will compute the mean {metric}{period_clause} for these {category}.",
        "I should determine the average {metric}{period_clause} for the selected {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        if not line_indices:
            reasoning = ["No lines available to calculate the average."]
            return OperatorResult(0.0, [], reasoning, [[]])
        mean_value = sum(self.line_values[i] for i in line_indices) / len(line_indices)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_plural,
            )
        ]
        return OperatorResult(mean_value, line_indices, reasoning, [line_indices])


class MedianOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate median {metric}{period_clause} for the selected {category}.",
        "I will find the middle {metric}{period_clause} for these {category}.",
        "I should determine the median {metric}{period_clause} for the selected {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        if not line_indices:
            reasoning = ["No lines available to calculate the median."]
            return OperatorResult(0.0, [], reasoning, [[]])
        sorted_pairs = sorted((self.line_values[i], i) for i in line_indices)
        n = len(sorted_pairs)
        if n % 2 == 1:
            median_value, median_idx = sorted_pairs[n // 2]
            indices = [median_idx]
        else:
            left_val, left_idx = sorted_pairs[n // 2 - 1]
            right_val, right_idx = sorted_pairs[n // 2]
            median_value = (left_val + right_val) / 2
            indices = sorted([left_idx, right_idx])
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_plural,
            )
        ]
        return OperatorResult(median_value, indices, reasoning, [line_indices, indices])


class CountOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to count the selected {category}.",
        "I will determine how many {category} are selected.",
        "I should compute the number of selected {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        count_value = len(line_indices)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(category=self.category_plural)
        ]
        return OperatorResult(count_value, line_indices, reasoning, [line_indices])


class ReadValueOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to read the {metric}{period_clause} for the selected {category}.",
        "I will extract the {metric}{period_clause} for these {category}.",
        "I should list the {metric}{period_clause} for the selected {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        values = [self.line_values[i] for i in line_indices]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_plural,
            )
        ]
        return OperatorResult(values, line_indices, reasoning, [line_indices])


class MaxOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to identify the {metric}{period_clause} that is the highest.",
        "I will look for the maximum {metric}{period_clause}.",
        "I should locate the {category} with the greatest {metric}{period_clause}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        if not line_indices:
            reasoning = ["No lines available to determine a maximum."]
            return OperatorResult(0.0, [], reasoning, [[]])
        values = [self.line_values[i] for i in line_indices]
        max_value = max(values)
        max_idx = line_indices[values.index(max_value)]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_singular,
            )
        ]
        return OperatorResult(max_value, [max_idx], reasoning, [line_indices, [max_idx]])


class MinOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to identify the {metric}{period_clause} that is the lowest.",
        "I will look for the minimum {metric}{period_clause}.",
        "I should locate the {category} with the smallest {metric}{period_clause}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        if not line_indices:
            reasoning = ["No lines available to determine a minimum."]
            return OperatorResult(0.0, [], reasoning, [[]])
        values = [self.line_values[i] for i in line_indices]
        min_value = min(values)
        min_idx = line_indices[values.index(min_value)]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_singular,
            )
        ]
        return OperatorResult(min_value, [min_idx], reasoning, [line_indices, [min_idx]])


class DifferenceOperator(LineZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate the difference in {metric}{period_clause} between the two selected {category}.",
        "I will compute the absolute difference in {metric}{period_clause}.",
        "I should find how far apart the {metric}{period_clause} values are for the selected {category}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None or len(line_indices) != 2:
            raise ValueError("DifferenceOperator requires exactly two line indices.")
        val1 = self.line_values[line_indices[0]]
        val2 = self.line_values[line_indices[1]]
        diff = abs(val1 - val2)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                category=self.category_plural,
            )
        ]
        return OperatorResult(diff, line_indices, reasoning, [line_indices])


class ThresholdOperator(LineOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to select {category} with {metric}{period_clause} {direction} {threshold}.",
        "I will filter {category} whose {metric}{period_clause} is {direction} {threshold}.",
        "I should keep {category} where {metric}{period_clause} is {direction} {threshold}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        direction = self.config.get("direction", "above")
        threshold = self.config.get("threshold", 0)
        if direction == "above":
            filtered = [i for i in line_indices if self.line_values[i] > threshold]
        else:
            filtered = [i for i in line_indices if self.line_values[i] < threshold]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                category=self.category_plural,
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
                direction=direction,
                threshold=threshold,
            )
        ]
        return OperatorResult(filtered, filtered, reasoning, [line_indices, filtered])


class KthOperator(LineOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to locate the {k}-th {direction} {metric}{period_clause}.",
        "I will identify the {k}-th {direction} {metric}{period_clause}.",
        "I should find the {k}-th {direction} {metric}{period_clause}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        direction = self.config.get("direction", "highest")
        k = self.config.get("k", 1)
        reverse = direction == "highest"
        pairs = sorted(((self.line_values[i], i) for i in line_indices), key=lambda x: x[0], reverse=reverse)
        if not pairs:
            reasoning = ["No lines available to select the requested rank."]
            return OperatorResult([], [], reasoning, [line_indices, []])
        index = max(0, min(k - 1, len(pairs) - 1))
        kth_value, kth_idx = pairs[index]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                k=f"{k}{self._ordinal_suffix(k)}",
                direction=direction,
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
            )
        ]
        return OperatorResult(kth_idx, [kth_idx], reasoning, [line_indices, [kth_idx]])

    @staticmethod
    def _ordinal_suffix(k: int) -> str:
        if 10 <= k % 100 <= 20:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")


class TopkOperator(LineOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to find the {direction} {k} {category} by {metric}{period_clause}.",
        "I will select the {direction} {k} {category} based on {metric}{period_clause}.",
        "I should identify the {direction} {k} {category} using {metric}{period_clause}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        direction = self.config.get("direction", "top")
        k = max(1, self.config.get("k", 1))
        reverse = direction == "top"
        pairs = sorted(((self.line_values[i], i) for i in line_indices), key=lambda x: x[0], reverse=reverse)
        selected = [idx for _, idx in pairs[:k]]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                direction="top" if direction == "top" else "bottom",
                k=k,
                category=self.category_plural,
                metric=self.metric_label.lower(),
                period_clause=self._period_clause(),
            )
        ]
        return OperatorResult(selected, selected, reasoning, [line_indices, selected])


class TakeAllOperator(LineOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to consider all {category}{period_clause}.",
        "I will include every {category}{period_clause}.",
    ]

    def apply(self, line_indices: List[int] = None) -> OperatorResult:
        if line_indices is None:
            line_indices = list(range(len(self.line_values)))
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                category=self.category_plural, period_clause=self._period_clause()
            )
        ]
        return OperatorResult(line_indices, line_indices, reasoning, [line_indices])


__all__ = [
    "LineOperator",
    "LineZeroStepOperator",
    "LineOneStepOperator",
    "SumOperator",
    "MeanOperator",
    "MedianOperator",
    "CountOperator",
    "ReadValueOperator",
    "MaxOperator",
    "MinOperator",
    "DifferenceOperator",
    "ThresholdOperator",
    "KthOperator",
    "TopkOperator",
    "TakeAllOperator",
]


