"""Operators tailored for heatmap QA generation."""

from __future__ import annotations

from abc import abstractmethod
from typing import Dict, List, Tuple
import sys
from pathlib import Path

try:
    from templates.operator import Operator, OperatorResult
except ImportError:  # pragma: no cover - fallback for isolated execution
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.operator import Operator, OperatorResult


class HeatmapOperator(Operator):
    """Base helper with heatmap-specific state and utilities."""

    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        super().__init__(chart_metadata, config, random_state)
        self.heatmap_data = self.chart_metadata.get("heatmap_data", [])
        self.x_labels = self.chart_metadata.get("x_labels", [])
        self.y_labels = self.chart_metadata.get("y_labels", [])
        self.heatmap_category = self.chart_metadata.get(
            "heatmap_category", {"singular": "value", "plural": "values"}
        )
        self.metric_singular = self.heatmap_category.get("singular", "value")
        self.metric_plural = self.heatmap_category.get("plural", "values")

        self.num_rows = len(self.heatmap_data)
        self.num_cols = len(self.heatmap_data[0]) if self.num_rows else 0
        self.total_cells = self.num_rows * self.num_cols
        self.flat_values = self._flatten_values()
        # Compatibility with base expectations
        self.bar_data = self.flat_values

    def _flatten_values(self) -> List[float]:
        flattened = []
        for row in self.heatmap_data:
            flattened.extend(row)
        return flattened

    def _default_indices(self) -> List[int]:
        return list(range(self.total_cells))

    def _idx_to_cell(self, idx: int) -> Tuple[int, int]:
        if self.num_cols == 0:
            return 0, 0
        return idx // self.num_cols, idx % self.num_cols

    def _describe_cell(self, idx: int) -> str:
        row, col = self._idx_to_cell(idx)
        row_label = self.y_labels[row] if 0 <= row < len(self.y_labels) else row
        col_label = self.x_labels[col] if 0 <= col < len(self.x_labels) else col
        return f"{row_label} vs {col_label}"


class HeatmapZeroStepOperator(HeatmapOperator):
    @abstractmethod
    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        raise NotImplementedError


class HeatmapOneStepOperator(HeatmapOperator):
    @abstractmethod
    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        raise NotImplementedError


class SumOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to add the {metric} across the selected cells.",
        "I will sum the {metric} for the chosen cells.",
        "I should compute the total {metric} for these cells.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        total = sum(self.flat_values[idx] for idx in cell_indices)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_plural)
        ]
        return OperatorResult(total, cell_indices, reasoning, [cell_indices])


class MeanOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate the average {metric} across the selected cells.",
        "I will compute the mean {metric} for these cells.",
        "I should determine the average {metric} for the chosen cells.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        if not cell_indices:
            reasoning = ["No cells were selected to calculate the average."]
            return OperatorResult(0.0, [], reasoning, [[]])
        mean_value = sum(self.flat_values[idx] for idx in cell_indices) / len(cell_indices)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_plural)
        ]
        return OperatorResult(mean_value, cell_indices, reasoning, [cell_indices])


class MedianOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to determine the median {metric} among the selected cells.",
        "I will find the middle {metric} for these cells.",
        "I should calculate the median {metric} of the chosen cells.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        if not cell_indices:
            reasoning = ["No cells were selected to calculate the median."]
            return OperatorResult(0.0, [], reasoning, [[]])
        sorted_pairs = sorted((self.flat_values[idx], idx) for idx in cell_indices)
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
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_plural)
        ]
        return OperatorResult(median_value, indices, reasoning, [cell_indices, indices])


class CountOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to count how many cells are selected.",
        "I will compute the number of selected cells.",
        "I should determine how many cells are included.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        count_value = len(cell_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(count_value, cell_indices, reasoning, [cell_indices])


class ReadValueOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to read the {metric} for the selected cells.",
        "I will report the {metric} at the chosen cells.",
        "I should list the {metric} values for these cells.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        values = [self.flat_values[idx] for idx in cell_indices]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_plural)
        ]
        return OperatorResult(values, cell_indices, reasoning, [cell_indices])


class MaxOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to identify the highest {metric} among the selected cells.",
        "I will look for the maximum {metric} in the chosen cells.",
        "I should find the cell with the largest {metric}.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        if not cell_indices:
            reasoning = ["No cells were selected to determine a maximum."]
            return OperatorResult(0.0, [], reasoning, [[]])
        values = [self.flat_values[idx] for idx in cell_indices]
        max_value = max(values)
        max_idx = cell_indices[values.index(max_value)]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_singular)
        ]
        reasoning.append(f"The maximum occurs at {self._describe_cell(max_idx)}.")
        return OperatorResult(max_value, [max_idx], reasoning, [cell_indices, [max_idx]])


class MinOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to identify the lowest {metric} among the selected cells.",
        "I will look for the minimum {metric} in the chosen cells.",
        "I should find the cell with the smallest {metric}.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        if not cell_indices:
            reasoning = ["No cells were selected to determine a minimum."]
            return OperatorResult(0.0, [], reasoning, [[]])
        values = [self.flat_values[idx] for idx in cell_indices]
        min_value = min(values)
        min_idx = cell_indices[values.index(min_value)]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_singular)
        ]
        reasoning.append(f"The minimum occurs at {self._describe_cell(min_idx)}.")
        return OperatorResult(min_value, [min_idx], reasoning, [cell_indices, [min_idx]])


class DifferenceOperator(HeatmapZeroStepOperator):
    REASONING_TEMPLATE = [
        "I need to calculate the difference between the two selected {metric}.",
        "I will compute the absolute difference of the selected cells.",
        "I should find how far apart the two {metric} values are.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None or len(cell_indices) != 2:
            raise ValueError("DifferenceOperator requires exactly two cell indices.")
        val1 = self.flat_values[cell_indices[0]]
        val2 = self.flat_values[cell_indices[1]]
        diff = abs(val1 - val2)
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(metric=self.metric_plural)
        ]
        return OperatorResult(diff, cell_indices, reasoning, [cell_indices])


class ThresholdOperator(HeatmapOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to select cells whose {metric} is {direction} {threshold}.",
        "I will filter cells with {metric} {direction} {threshold}.",
        "I should find cells where {metric} is {direction} {threshold}.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        direction = self.config.get("direction", "above")
        threshold = self.config.get("threshold", 0)
        if direction == "above":
            filtered = [idx for idx in cell_indices if self.flat_values[idx] > threshold]
        else:
            filtered = [idx for idx in cell_indices if self.flat_values[idx] < threshold]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                metric=self.metric_plural, direction=direction, threshold=threshold
            )
        ]
        return OperatorResult(filtered, filtered, reasoning, [cell_indices, filtered])


class KthOperator(HeatmapOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to locate the {k}-th {direction} {metric} among the selected cells.",
        "I will identify the {k}-th {direction} {metric} cell.",
        "I should find the {k}-th {direction} {metric} cell.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        direction = self.config.get("direction", "highest")
        k = max(1, self.config.get("k", 1))
        reverse = direction == "highest"
        pairs = sorted(((self.flat_values[idx], idx) for idx in cell_indices), key=lambda x: x[0], reverse=reverse)
        if not pairs:
            reasoning = ["No cells available to locate the requested rank."]
            return OperatorResult([], [], reasoning, [cell_indices, []])
        index = max(0, min(k - 1, len(pairs) - 1))
        kth_value, kth_idx = pairs[index]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                k=f"{k}{self._ordinal_suffix(k)}", direction=direction, metric=self.metric_plural
            )
        ]
        reasoning.append(f"The cell corresponds to {self._describe_cell(kth_idx)}.")
        return OperatorResult(kth_idx, [kth_idx], reasoning, [cell_indices, [kth_idx]])

    @staticmethod
    def _ordinal_suffix(k: int) -> str:
        if 10 <= k % 100 <= 20:
            return "th"
        return {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")


class TopkOperator(HeatmapOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to select the {direction} {k} cells by {metric}.",
        "I will find the {direction} {k} cells using {metric}.",
        "I should identify the {direction} {k} cells respected to {metric}.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        direction = self.config.get("direction", "top")
        k = max(1, self.config.get("k", 1))
        reverse = direction == "top"
        pairs = sorted(((self.flat_values[idx], idx) for idx in cell_indices), key=lambda x: x[0], reverse=reverse)
        selected = [idx for _, idx in pairs[:k]]
        reasoning = [
            self.random_state.choice(self.REASONING_TEMPLATE).format(
                direction="top" if direction == "top" else "bottom",
                k=k,
                metric=self.metric_plural,
            )
        ]
        return OperatorResult(selected, selected, reasoning, [cell_indices, selected])


class TakeAllOperator(HeatmapOneStepOperator):
    REASONING_TEMPLATE = [
        "I need to include all cells.",
        "I will take every cell in the grid.",
    ]

    def apply(self, cell_indices: List[int] = None) -> OperatorResult:
        if cell_indices is None:
            cell_indices = self._default_indices()
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(cell_indices, cell_indices, reasoning, [cell_indices])


__all__ = [
    "HeatmapOperator",
    "HeatmapZeroStepOperator",
    "HeatmapOneStepOperator",
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


