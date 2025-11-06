from typing import List, Dict, Any
from abc import abstractmethod
import sys
from pathlib import Path

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
    """Abstract base class for zero-step operators: h(list[Bar]) -> list[v]"""
    
    @abstractmethod
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified bar indices."""
        pass

class SumOperator(ZeroStepOperator):
    """Zero-step operator for sum operation."""

    REASONING_TEMPLATE = [
        "I need to calculate sum of {y_label} for given bars.",
        "I will compute the total {y_label} for the specified bars.",
        "I should add up all the {y_label} values for these bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Compute and explain sum of list elements."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        total = sum([self.bar_data[i] for i in bar_indices])
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(total, bar_indices, reasoning, [])

class MeanOperator(ZeroStepOperator):
    """Zero-step operator for mean operation."""

    REASONING_TEMPLATE = [
        "I need to calculate mean of {y_label} for given bars.",
        "I will compute the average {y_label} for the specified bars.",
        "I should find the mean value of {y_label} for these bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Compute and explain mean of list elements."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        mean_value = sum([self.bar_data[i] for i in bar_indices]) / len(bar_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(mean_value, bar_indices, reasoning, [])

class MedianOperator(ZeroStepOperator):
    """Zero-step operator for median operation."""

    REASONING_TEMPLATE = [
        "I need to calculate median of {y_label} for given bars.",
        "I will find the middle value of {y_label} for these bars.",
        "I should determine the median {y_label} for the specified bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Compute and explain median of list elements."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        sorted_data = sorted([self.bar_data[i] for i in bar_indices])
        n = len(sorted_data)
        
        if n % 2 == 1:
            median_value = sorted_data[n // 2]
        else:
            median_value = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
            
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(median_value, bar_indices, reasoning, [])

class CountOperator(ZeroStepOperator):
    """Zero-step operator for count operation."""

    REASONING_TEMPLATE = [
        "I need to count the number of bars.",
        "I will count how many bars are specified.",
        "I should determine the total number of bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Compute and explain count of list elements."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        count_value = len(bar_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(count_value, bar_indices, reasoning, [])

class ReadValueOperator(ZeroStepOperator):
    """Read value of the given bar"""

    REASONING_TEMPLATE = [
        "I need to read the {y_label} of the given bars.",
        "I will extract the {y_label} values from these bars.",
        "I should get the {y_label} for the specified bars.",
    ]

    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Read value of the given bar."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        values = [self.bar_data[i] for i in bar_indices]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(values, bar_indices, reasoning, [])

class MaxOperator(ZeroStepOperator):
    """Find maximum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the maximum {y_label}.",
        "I will identify the highest {y_label}.",
        "I should locate the maximum {y_label}.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Find maximum value."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        values = [self.bar_data[i] for i in bar_indices]
        max_value = max(values)
        max_idx = bar_indices[values.index(max_value)]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(max_value, [max_idx], reasoning, [])

class MinOperator(ZeroStepOperator):
    """Find minimum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the minimum {y_label}.",
        "I will identify the lowest {y_label}.",
        "I should locate the minimum {y_label}.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Find minimum value."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        values = [self.bar_data[i] for i in bar_indices]
        min_value = min(values)
        min_idx = bar_indices[values.index(min_value)]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(y_label=self.y_label.lower())]
        return OperatorResult(min_value, [min_idx], reasoning, [])

class DifferenceOperator(ZeroStepOperator):
    """Calculate difference between two values."""
    
    REASONING_TEMPLATE = [
        "I need to calculate the difference between the two values.",
        "I will compute the absolute difference.",
        "I should find the difference between these values.",
    ]
    
    def apply(self, bar_indices: List[int]) -> OperatorResult:
        """Calculate difference between values at indices."""
        assert len(bar_indices) == 2, "DifferenceOperator requires exactly 2 indices"
        val1, val2 = self.bar_data[bar_indices[0]], self.bar_data[bar_indices[1]]
        diff = abs(val1 - val2)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(diff, bar_indices, reasoning, [])

# ============================================================
#                        One-step Operators
# ============================================================

class OneStepOperator(Operator):
    """Abstract base class for one-step operators: f(list[Bar]) -> list[Bar]"""
    
    @abstractmethod
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified bar indices."""
        pass

class ThresholdOperator(OneStepOperator):
    """Filter bars based on a condition."""
    
    REASONING_TEMPLATE = [
        "I need to filter bars based on the condition: {condition}.",
        "I will select bars that meet the condition: {condition}.",
        "I should find bars matching the condition: {condition}.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Filter bars based on condition."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        
        threshold = self.config.get("threshold", 0)
        direction = self.config.get("direction", "above")
        
        # Generate condition string from direction and threshold
        condition = f"{direction} {threshold}"
        
        if direction == "above":
            filtered_indices = [i for i in bar_indices if self.bar_data[i] > threshold]
        else:
            filtered_indices = [i for i in bar_indices if self.bar_data[i] < threshold]
        
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(condition=condition)]
        return OperatorResult(filtered_indices, filtered_indices, reasoning, [bar_indices, filtered_indices])

class KthOperator(OneStepOperator):
    """Find k-th highest/lowest bar"""

    REASONING_TEMPLATE = [
        "I need to find the {k}-th {direction} bar.",
        "I will locate the {k}-th {direction} bar by value.",
        "I should identify the {k}-th {direction} bar.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Find k-th highest/lowest bar."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        
        value_index_pairs = [(self.bar_data[i], i) for i in bar_indices]
        direction = self.config.get("direction", "highest")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "highest"))
        
        k = self.config.get("k", 1)
        assert 1 <= k <= len(sorted_pairs), f"k must be between 1 and {len(sorted_pairs)}"
        
        kth_value, kth_index = sorted_pairs[k - 1]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(kth_index, [kth_index], reasoning, [bar_indices, [kth_index]])
    
class TopkOperator(OneStepOperator):
    """Find top/bottom k bars"""

    REASONING_TEMPLATE = [
        "I need to find the {direction} {k} bars.",
        "I will locate the {direction} {k} bars by value.",
        "I should identify the {direction} {k} bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Find top/bottom k bars."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        
        value_index_pairs = [(self.bar_data[i], i) for i in bar_indices]
        direction = self.config.get("direction", "top")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "top"))
        
        k = self.config.get("k", 1)
        assert 1 <= k <= len(sorted_pairs), f"k must be between 1 and {len(sorted_pairs)}"
        
        indices = [pair[1] for pair in sorted_pairs[:k]]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(indices, indices, reasoning, [bar_indices, indices])


class TakeAllOperator(OneStepOperator):
    """Take all bars"""
    
    REASONING_TEMPLATE = [
        "I need to take all bars.",
        "I will select all bars.",
    ]
    
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Take all bars."""
        if bar_indices is None:
            bar_indices = list(range(len(self.bar_data)))
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(bar_indices, bar_indices, reasoning, [bar_indices])

# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_chart_metadata = {
        'bar_data': [10, 25, 15, 30, 20, 35, 12, 28],
        'bar_labels': ["A", "B", "C", "D", "E", "F", "G", "H"],
        'x_label': 'Category',
        'y_label': 'Revenue',
        'chart_direction': 'vertical'
    }
    
    print("=== Simplified Operator Composition Test ===")
    print(f"Sample Data: {sample_chart_metadata['bar_data']}")
    print()
    
    # Create basic operators with metadata
    sum_op = SumOperator(sample_chart_metadata)
    read_op = ReadValueOperator(sample_chart_metadata)
    mean_op = MeanOperator(sample_chart_metadata)
    filter_op = ThresholdOperator(sample_chart_metadata, {"condition": "above 20", "threshold": 20, "direction": "above"})
    max_op = MaxOperator(sample_chart_metadata)
    min_op = MinOperator(sample_chart_metadata)
    diff_op = DifferenceOperator(sample_chart_metadata)
    kth_op = KthOperator(sample_chart_metadata, {"k": 2, "direction": "highest"})
    take_all_op = TakeAllOperator(sample_chart_metadata)
    top_k_max = TopkOperator(sample_chart_metadata, {"k": 1, "direction": "top"})
    top_k_min = TopkOperator(sample_chart_metadata, {"k": 1, "direction": "bottom"})
    
    print("--- Testing Zero-step Operations with TakeAllOperator ---")
    # Use TakeAllOperator for zero-step operations (sequential composition)
    mean_all_op = mean_op(take_all_op)
    mean_result = mean_all_op()
    print(f"Mean of all bars: {mean_result}")
    
    # Alternative: Direct usage with default bar_indices
    mean_result2 = mean_op()
    print(f"Mean (direct): {mean_result2}")
    
    print("\n--- Testing Sequential Composition: op_a(op_b) ---")
    # Sequential composition: sum of filtered values
    sum_of_filtered = sum_op(filter_op)
    result1 = sum_of_filtered()
    print(f"Sum of filtered: {result1}")
    
    print("\n--- Testing Parallel Composition: op_a(op_b, op_c) ---")
    # Parallel composition: difference between max and min values
    range_op = diff_op(top_k_max, top_k_min)
    result2 = range_op()
    print(f"Range (max - min): {result2}")
    
    print("\n--- Testing Nested Composition: op_a(op_b(op_c)) ---")
    # Nested composition: value at k-th position of filtered results
    nested_op = read_op(kth_op(filter_op))
    result3 = nested_op()
    print(f"Max of kth of filtered: {result3}")
    
    print("\n=== Test Complete ===")

