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
    """Abstract base class for zero-step operators: h(list[Pie]) -> value or list[value]"""
    
    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        """Initialize with pie chart metadata."""
        super().__init__(chart_metadata, config, random_state)
        self.pie_data = self.chart_metadata.get('pie_data', [])
        self.pie_labels = self.chart_metadata.get('pie_labels', [])
        self.pie_data_category = self.chart_metadata.get('pie_data_category', {"singular": "value", "plural": "values"})
        self.pie_label_category = self.chart_metadata.get('pie_label_category', {"singular": "category", "plural": "categories"})
        # For compatibility with base class
        self.bar_data = self.pie_data
    
    @abstractmethod
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified pie slice indices."""
        pass


class OneStepOperator(Operator):
    """Abstract base class for one-step operators: f(list[Pie]) -> list[Pie]"""
    
    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        """Initialize with pie chart metadata."""
        super().__init__(chart_metadata, config, random_state)
        self.pie_data = self.chart_metadata.get('pie_data', [])
        self.pie_labels = self.chart_metadata.get('pie_labels', [])
        self.pie_data_category = self.chart_metadata.get('pie_data_category', {"singular": "value", "plural": "values"})
        self.pie_label_category = self.chart_metadata.get('pie_label_category', {"singular": "category", "plural": "categories"})
        # For compatibility with base class
        self.bar_data = self.pie_data
    
    @abstractmethod
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified pie slice indices."""
        pass


# ============================================================
#                        Zero-step Operators
# ============================================================

class SumOperator(ZeroStepOperator):
    """Zero-step operator for sum operation."""

    REASONING_TEMPLATE = [
        "I need to calculate sum of {data_category} for given slices.",
        "I will compute the total {data_category} for the specified slices.",
        "I should add up all the {data_category} values for these slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Compute and explain sum of list elements."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        total = sum([self.pie_data[i] for i in pie_indices])
        data_category = self.pie_data_category.get('plural', 'values')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(total, pie_indices, reasoning, [pie_indices])


class MeanOperator(ZeroStepOperator):
    """Zero-step operator for mean operation."""

    REASONING_TEMPLATE = [
        "I need to calculate mean of {data_category} for given slices.",
        "I will compute the average {data_category} for the specified slices.",
        "I should find the mean value of {data_category} for these slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Compute and explain mean of list elements."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            return OperatorResult(0, [], ["Cannot compute mean of empty list"], [])
        mean_value = sum([self.pie_data[i] for i in pie_indices]) / len(pie_indices)
        data_category = self.pie_data_category.get('plural', 'values')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(mean_value, pie_indices, reasoning, [pie_indices])


class MedianOperator(ZeroStepOperator):
    """Zero-step operator for median operation."""

    REASONING_TEMPLATE = [
        "I need to calculate median of {data_category} for given slices.",
        "I will find the middle value of {data_category} for these slices.",
        "I should determine the median {data_category} for the specified slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Compute and explain median of list elements."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            return OperatorResult(0, [], ["Cannot compute median of empty list"], [])
        
        sorted_data_with_indices = sorted([(self.pie_data[i], i) for i in pie_indices], key=lambda x: x[0])
        n = len(sorted_data_with_indices)
        
        if n % 2 == 1:
            median_value = sorted_data_with_indices[n // 2][0]
            median_result_indices = [sorted_data_with_indices[n // 2][1]]
        else:
            mid1_val, mid1_idx = sorted_data_with_indices[n // 2 - 1]
            mid2_val, mid2_idx = sorted_data_with_indices[n // 2]
            median_value = (mid1_val + mid2_val) / 2
            median_result_indices = sorted([mid1_idx, mid2_idx])
            
        data_category = self.pie_data_category.get('plural', 'values')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(median_value, median_result_indices, reasoning, [pie_indices, median_result_indices])


class CountOperator(ZeroStepOperator):
    """Zero-step operator for count operation."""

    REASONING_TEMPLATE = [
        "I need to count the number of slices.",
        "I will count how many slices are specified.",
        "I should determine the total number of slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Compute and explain count of list elements."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        count_value = len(pie_indices)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(count_value, pie_indices, reasoning, [pie_indices])


class ReadValueOperator(ZeroStepOperator):
    """Read value of the given slice"""

    REASONING_TEMPLATE = [
        "I need to read the {data_category} of the given slices.",
        "I will extract the {data_category} values from these slices.",
        "I should get the {data_category} for the specified slices.",
    ]

    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Read value of the given slice."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        values = [self.pie_data[i] for i in pie_indices]
        data_category = self.pie_data_category.get('plural', 'values')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(values, pie_indices, reasoning, [pie_indices])


class MaxOperator(ZeroStepOperator):
    """Find maximum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the maximum {data_category}.",
        "I will identify the highest {data_category}.",
        "I should locate the maximum {data_category}.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Find maximum value."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            return OperatorResult(0, [], ["Cannot find max of empty list"], [])
        values = [self.pie_data[i] for i in pie_indices]
        max_value = max(values)
        max_indices = [pie_indices[i] for i, v in enumerate(values) if v == max_value]
        data_category = self.pie_data_category.get('singular', 'value')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(max_value, max_indices, reasoning, [pie_indices, max_indices])


class MinOperator(ZeroStepOperator):
    """Find minimum value."""
    
    REASONING_TEMPLATE = [
        "I need to find the minimum {data_category}.",
        "I will identify the lowest {data_category}.",
        "I should locate the minimum {data_category}.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Find minimum value."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            return OperatorResult(0, [], ["Cannot find min of empty list"], [])
        values = [self.pie_data[i] for i in pie_indices]
        min_value = min(values)
        min_indices = [pie_indices[i] for i, v in enumerate(values) if v == min_value]
        data_category = self.pie_data_category.get('singular', 'value')
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(data_category=data_category)]
        return OperatorResult(min_value, min_indices, reasoning, [pie_indices, min_indices])


class DifferenceOperator(ZeroStepOperator):
    """Calculate difference between two values."""
    
    REASONING_TEMPLATE = [
        "I need to calculate the difference between the two values.",
        "I will compute the absolute difference.",
        "I should find the difference between these values.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Calculate difference between values at indices."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        
        if len(pie_indices) > 2:
            pie_indices = pie_indices[:2]
        elif len(pie_indices) < 2:
            raise ValueError("DifferenceOperator requires at least 2 indices")
        
        val1, val2 = self.pie_data[pie_indices[0]], self.pie_data[pie_indices[1]]
        diff = abs(val1 - val2)
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(diff, pie_indices, reasoning, [pie_indices])


# ============================================================
#                        One-step Operators
# ============================================================

class ThresholdOperator(OneStepOperator):
    """Filter slices based on a condition."""
    
    REASONING_TEMPLATE = [
        "I need to filter slices based on the condition: {condition}.",
        "I will select slices that meet the condition: {condition}.",
        "I should find slices matching the condition: {condition}.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Filter slices based on condition."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        
        threshold = self.config.get("threshold", 0)
        direction = self.config.get("direction", "above")
        
        condition = f"{direction} {threshold}"
        
        if direction == "above":
            filtered_indices = [i for i in pie_indices if self.pie_data[i] > threshold]
        else:
            filtered_indices = [i for i in pie_indices if self.pie_data[i] < threshold]
        
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(condition=condition)]
        return OperatorResult(filtered_indices, filtered_indices, reasoning, [pie_indices, filtered_indices])


class KthOperator(OneStepOperator):
    """Find k-th highest/lowest slice"""

    REASONING_TEMPLATE = [
        "I need to find the {k}-th {direction} slice.",
        "I will locate the {k}-th {direction} slice by value.",
        "I should identify the {k}-th {direction} slice.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Find k-th highest/lowest slice."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            raise ValueError("Cannot find k-th element in an empty list")
        
        value_index_pairs = [(self.pie_data[i], i) for i in pie_indices]
        direction = self.config.get("direction", "highest")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "highest"))
        
        k = self.config.get("k", 1)
        if k < 1 or k > len(sorted_pairs):
            raise ValueError(f"k must be between 1 and {len(sorted_pairs)}")
        
        kth_value, kth_index = sorted_pairs[k - 1]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(kth_index, [kth_index], reasoning, [pie_indices, [kth_index]])
    
class TopkOperator(OneStepOperator):
    """Find top/bottom k slices"""

    REASONING_TEMPLATE = [
        "I need to find the {direction} {k} slices.",
        "I will locate the {direction} {k} slices by value.",
        "I should identify the {direction} {k} slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Find top/bottom k slices."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        if not pie_indices:
            return OperatorResult([], [], ["Cannot find top/bottom k in an empty list"], [])
        
        value_index_pairs = [(self.pie_data[i], i) for i in pie_indices]
        direction = self.config.get("direction", "top")
        sorted_pairs = sorted(value_index_pairs, key=lambda x: x[0], reverse=(direction == "top"))
        
        k = self.config.get("k", 1)
        if k < 1 or k > len(sorted_pairs):
            raise ValueError(f"k must be between 1 and {len(sorted_pairs)}")
        
        indices = [pair[1] for pair in sorted_pairs[:k]]
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE).format(k=k, direction=direction)]
        return OperatorResult(indices, indices, reasoning, [pie_indices, indices])


class TakeAllOperator(OneStepOperator):
    """Take all slices"""
    
    REASONING_TEMPLATE = [
        "I need to take all slices.",
        "I will select all slices.",
    ]
    
    def apply(self, pie_indices: List[int] = None) -> OperatorResult:
        """Take all slices."""
        if pie_indices is None:
            pie_indices = list(range(len(self.pie_data)))
        reasoning = [self.random_state.choice(self.REASONING_TEMPLATE)]
        return OperatorResult(pie_indices, pie_indices, reasoning, [pie_indices])


# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_chart_metadata = {
        'pie_data': [35, 25, 20, 15, 5],
        'pie_labels': ["Technology", "Healthcare", "Finance", "Education", "Others"],
        'pie_data_category': {"singular": "market share", "plural": "market shares"},
        'pie_label_category': {"singular": "sector", "plural": "sectors"},
        'img_title': "Market Share Distribution by Sector"
    }
    
    print("=== Pie Chart Operator Test ===")
    print(f"Sample Data: {sample_chart_metadata['pie_data']}")
    print()
    
    # Create basic operators with metadata
    sum_op = SumOperator(sample_chart_metadata)
    read_op = ReadValueOperator(sample_chart_metadata)
    mean_op = MeanOperator(sample_chart_metadata)
    filter_op = ThresholdOperator(sample_chart_metadata, {"threshold": 20, "direction": "above"})
    max_op = MaxOperator(sample_chart_metadata)
    min_op = MinOperator(sample_chart_metadata)
    diff_op = DifferenceOperator(sample_chart_metadata)
    kth_op = KthOperator(sample_chart_metadata, {"k": 2, "direction": "highest"})
    take_all_op = TakeAllOperator(sample_chart_metadata)
    top_k_max = TopkOperator(sample_chart_metadata, {"k": 1, "direction": "top"})
    top_k_min = TopkOperator(sample_chart_metadata, {"k": 1, "direction": "bottom"})
    
    print("--- Testing Zero-step Operations ---")
    # Use TakeAllOperator for zero-step operations (sequential composition)
    mean_all_op = mean_op(take_all_op)
    mean_result = mean_all_op()
    print(f"Mean of all slices: {mean_result}")
    
    # Alternative: Direct usage with default pie_indices
    mean_result2 = mean_op()
    print(f"Mean (direct): {mean_result2}")
    
    print("\n--- Testing Sequential Composition: op_a(op_b) ---")
    # Sequential composition: sum of filtered values
    sum_of_filtered = sum_op(filter_op)
    result1 = sum_of_filtered()
    print(f"Sum of filtered: {result1}")
    
    print("\n--- Testing Parallel Composition: op_a(op_b, op_c) ---")
    # Parallel composition: difference between max and min values
    # Note: diff needs exactly 2 indices, so we use kth operators that return single indices
    kth_max = KthOperator(chart_metadata=sample_chart_metadata, config={"k": 1, "direction": "highest"})
    kth_min = KthOperator(chart_metadata=sample_chart_metadata, config={"k": 1, "direction": "lowest"})
    range_op = diff_op(kth_max, kth_min)
    result2 = range_op()
    print(f"Range (max - min): {result2}")
    
    print("\n--- Testing Nested Composition: op_a(op_b(op_c)) ---")
    # Nested composition: value at k-th position of filtered results
    nested_op = read_op(kth_op(filter_op))
    result3 = nested_op()
    print(f"Value of kth of filtered: {result3}")
    
    print("\n=== Test Complete ===")


