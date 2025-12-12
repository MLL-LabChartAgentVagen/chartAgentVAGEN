from typing import List, Dict, Any
from abc import abstractmethod
import sys
from pathlib import Path
import random

# Import base classes from templates
# Handle both direct execution and module import
try:
    from templates.operator import Operator, OperatorResult
except ImportError:
    # Fallback: add project root to path if package structure isn't set up
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.operator import Operator, OperatorResult


class ZeroStepOperator(Operator):
    """Abstract base class for zero-step operators: h(list[Scatter]) -> value or list[value]"""
    
    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        """Initialize with scatter chart metadata."""
        super().__init__(chart_metadata, config, random_state)
        self.scatter_x_data = self.chart_metadata.get('scatter_x_data', [])
        self.scatter_y_data = self.chart_metadata.get('scatter_y_data', [])
        self.scatter_labels = self.chart_metadata.get('scatter_labels', [])
        # For compatibility with base class
        self.bar_data = self.scatter_x_data  # Default to x_data
    
    @abstractmethod
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified scatter point indices."""
        pass


class OneStepOperator(Operator):
    """Abstract base class for one-step operators: f(list[Scatter]) -> list[Scatter]"""
    
    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        """Initialize with scatter chart metadata."""
        super().__init__(chart_metadata, config, random_state)
        self.scatter_x_data = self.chart_metadata.get('scatter_x_data', [])
        self.scatter_y_data = self.chart_metadata.get('scatter_y_data', [])
        self.scatter_labels = self.chart_metadata.get('scatter_labels', [])
        # For compatibility with base class
        self.bar_data = self.scatter_x_data  # Default to x_data
    
    @abstractmethod
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified scatter point indices."""
        pass


# ============================================================
#                        Zero-step Operators
# ============================================================

class SumOperator(ZeroStepOperator):
    """Zero-step operator for sum operation."""

    REASONING_TEMPLATE = [
        "I need to calculate sum of {axis_label} for given scatter points.",
        "I will compute the total {axis_label} for the specified scatter points.",
        "I should add up all the {axis_label} values for these scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Compute and explain sum of list elements."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        total = sum([data[i] for i in scatter_indices])
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(total, scatter_indices, reasoning, [scatter_indices])


class MeanOperator(ZeroStepOperator):
    """Zero-step operator for mean operation."""

    REASONING_TEMPLATE = [
        "I need to calculate mean of {axis_label} for given scatter points.",
        "I will compute the average {axis_label} for the specified scatter points.",
        "I should find the mean value of {axis_label} for these scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Compute and explain mean of list elements."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            return OperatorResult(0, [], ["Cannot compute mean of empty list"], [])
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        mean_value = sum([data[i] for i in scatter_indices]) / len(scatter_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(mean_value, scatter_indices, reasoning, [scatter_indices])


class MedianOperator(ZeroStepOperator):
    """Zero-step operator for median operation."""

    REASONING_TEMPLATE = [
        "I need to calculate median of {axis_label} for given scatter points.",
        "I will find the middle value of {axis_label} for these scatter points.",
        "I should determine the median {axis_label} for the specified scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Compute and explain median of list elements."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            return OperatorResult(0, [], ["Cannot compute median of empty list"], [])
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        sorted_data_with_indices = sorted([(data[i], i) for i in scatter_indices], key=lambda x: x[0])
        n = len(sorted_data_with_indices)
        
        if n % 2 == 1:
            median_value = sorted_data_with_indices[n // 2][0]
            median_result_indices = [sorted_data_with_indices[n // 2][1]]
        else:
            mid1_val, mid1_idx = sorted_data_with_indices[n // 2 - 1]
            mid2_val, mid2_idx = sorted_data_with_indices[n // 2]
            median_value = (mid1_val + mid2_val) / 2
            median_result_indices = sorted([mid1_idx, mid2_idx])
            
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(median_value, median_result_indices, reasoning, [scatter_indices, median_result_indices])


class CountOperator(ZeroStepOperator):
    """Zero-step operator for count operation."""

    REASONING_TEMPLATE = [
        "I need to count the number of scatter points.",
        "I will count how many scatter points are specified.",
        "I should determine the total number of scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Compute and explain count of list elements."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        count_value = len(scatter_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(count_value, scatter_indices, reasoning, [scatter_indices])


class ReadValueOperator(ZeroStepOperator):
    """Read value of the given scatter point"""

    REASONING_TEMPLATE = [
        "I need to read the {axis_label} of the given scatter points.",
        "I will extract the {axis_label} values from these scatter points.",
        "I should get the {axis_label} for the specified scatter points.",
    ]

    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Read value of the given scatter point."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        values = [data[i] for i in scatter_indices]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(values, scatter_indices, reasoning, [scatter_indices])


class ReadLabelOperator(ZeroStepOperator):
    """Read label of the given scatter point"""

    REASONING_TEMPLATE = [
        "I need to read the label of the given scatter points.",
        "I will extract the labels from these scatter points.",
        "I should get the labels for the specified scatter points.",
    ]

    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Read label of the given scatter point."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        
        labels = [self.scatter_labels[i] for i in scatter_indices]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(labels, scatter_indices, reasoning, [scatter_indices])


class MaxOperator(ZeroStepOperator):
    """Find maximum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the maximum {axis_label}.",
        "I will identify the highest {axis_label}.",
        "I should locate the maximum {axis_label}.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Find maximum value."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            return OperatorResult(0, [], ["Cannot find max of empty list"], [])
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        values = [data[i] for i in scatter_indices]
        max_value = max(values)
        max_indices = [scatter_indices[i] for i, v in enumerate(values) if v == max_value]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(max_value, max_indices, reasoning, [scatter_indices, max_indices])


class MinOperator(ZeroStepOperator):
    """Find minimum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the minimum {axis_label}.",
        "I will identify the lowest {axis_label}.",
        "I should locate the minimum {axis_label}.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Find minimum value."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            return OperatorResult(0, [], ["Cannot find min of empty list"], [])
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        values = [data[i] for i in scatter_indices]
        min_value = min(values)
        min_indices = [scatter_indices[i] for i, v in enumerate(values) if v == min_value]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(axis_label=axis_label)]
        return OperatorResult(min_value, min_indices, reasoning, [scatter_indices, min_indices])


class DifferenceOperator(ZeroStepOperator):
    """Calculate difference between two values."""
    
    REASONING_TEMPLATE = [
        "I need to calculate the difference between the two values.",
        "I will compute the absolute difference.",
        "I should find the difference between these values.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Calculate difference between values at indices."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        
        if len(scatter_indices) > 2:
            scatter_indices = scatter_indices[:2]
        elif len(scatter_indices) < 2:
            raise ValueError("DifferenceOperator requires at least 2 indices")
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        
        val1, val2 = data[scatter_indices[0]], data[scatter_indices[1]]
        diff = abs(val1 - val2)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(diff, scatter_indices, reasoning, [scatter_indices])


# ============================================================
#                        One-step Operators
# ============================================================

class ThresholdOperator(OneStepOperator):
    """Filter scatter points based on a condition."""
    
    REASONING_TEMPLATE = [
        "I need to filter scatter points based on the condition: {condition}.",
        "I will select scatter points that meet the condition: {condition}.",
        "I should find scatter points matching the condition: {condition}.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Filter scatter points based on condition."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        
        threshold = self.config.get("threshold", 0)
        direction = self.config.get("direction", "above")
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        
        condition = f"{direction} {threshold}"
        
        if direction == "above":
            filtered_indices = [i for i in scatter_indices if data[i] > threshold]
        else:
            filtered_indices = [i for i in scatter_indices if data[i] < threshold]
        
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(condition=condition)]
        return OperatorResult(filtered_indices, filtered_indices, reasoning, [scatter_indices, filtered_indices])


class KthOperator(OneStepOperator):
    """Find k-th highest/lowest scatter point"""

    REASONING_TEMPLATE = [
        "I need to find the {k}-th {direction} scatter point.",
        "I will locate the {k}-th {direction} scatter point by value.",
        "I should identify the {k}-th {direction} scatter point.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Find k-th highest/lowest scatter point."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            raise ValueError("Cannot find k-th element in an empty list")
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        
        value_index_pairs = [(data[i], i) for i in scatter_indices]
        direction = self.config.get("direction", "highest")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "highest"))
        
        k = self.config.get("k", 1)
        if k < 1 or k > len(sorted_pairs):
            raise ValueError(f"k must be between 1 and {len(sorted_pairs)}")
        
        kth_value, kth_index = sorted_pairs[k - 1]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(kth_index, [kth_index], reasoning, [scatter_indices, [kth_index]])
    
class TopkOperator(OneStepOperator):
    """Find top/bottom k scatter points"""

    REASONING_TEMPLATE = [
        "I need to find the {direction} {k} scatter points.",
        "I will locate the {direction} {k} scatter points by value.",
        "I should identify the {direction} {k} scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Find top/bottom k scatter points."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        if not scatter_indices:
            return OperatorResult([], [], ["Cannot find top/bottom k in an empty list"], [])
        
        axis = self.config.get("axis", "x")  # "x" or "y"
        data = self.scatter_x_data if axis == "x" else self.scatter_y_data
        
        value_index_pairs = [(data[i], i) for i in scatter_indices]
        direction = self.config.get("direction", "top")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "top"))
        
        k = self.config.get("k", 1)
        if k < 1 or k > len(sorted_pairs):
            raise ValueError(f"k must be between 1 and {len(sorted_pairs)}")
        
        indices = [pair[1] for pair in sorted_pairs[:k]]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(indices, indices, reasoning, [scatter_indices, indices])


class TakeAllOperator(OneStepOperator):
    """Take all scatter points"""
    
    REASONING_TEMPLATE = [
        "I need to take all scatter points.",
        "I will select all scatter points.",
    ]
    
    def apply(self, scatter_indices: List[int] = None) -> OperatorResult:
        """Take all scatter points."""
        if scatter_indices is None:
            scatter_indices = list(range(len(self.scatter_x_data)))
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(scatter_indices, scatter_indices, reasoning, [scatter_indices])


# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_chart_metadata = {
        'scatter_x_data': [1.2, 2.5, 3.8, 4.1, 5.3],
        'scatter_y_data': [22.75, 32.43, 33.96, 45.36, 19.32],
        'scatter_labels': ["A", "B", "C", "D", "E"],
        'x_label': 'Rating Score',
        'y_label': 'Box Office Earnings',
    }
    
    print("=== Scatter Chart Operator Test ===")
    print(f"Sample X Data: {sample_chart_metadata['scatter_x_data']}")
    print(f"Sample Y Data: {sample_chart_metadata['scatter_y_data']}")
    print()
    
    # Create basic operators with metadata
    sum_op_x = SumOperator(sample_chart_metadata, {"axis": "x"})
    mean_op_y = MeanOperator(sample_chart_metadata, {"axis": "y"})
    filter_op = ThresholdOperator(sample_chart_metadata, {"threshold": 3.0, "direction": "above", "axis": "x"})
    max_op = MaxOperator(sample_chart_metadata, {"axis": "x"})
    min_op = MinOperator(sample_chart_metadata, {"axis": "y"})
    read_label_op = ReadLabelOperator(sample_chart_metadata)
    take_all_op = TakeAllOperator(sample_chart_metadata)
    
    print("--- Testing Zero-step Operations ---")
    mean_all_op = mean_op_y(take_all_op)
    mean_result = mean_all_op()
    print(f"Mean of all y values: {mean_result}")
    
    print("\n--- Testing Sequential Composition: op_a(op_b) ---")
    sum_of_filtered = sum_op_x(filter_op)
    result1 = sum_of_filtered()
    print(f"Sum of filtered x values: {result1}")
    
    print("\n--- Testing Read Label ---")
    label_result = read_label_op()
    print(f"Labels: {label_result}")
    
    print("\n=== Test Complete ===")

