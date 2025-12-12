from typing import List, Dict, Any, Union, Optional, Callable
from abc import ABC, abstractmethod
import copy
import random
from dataclasses import dataclass, field


"""
Define operator for bar chart
Bar Chart Operators:

1. Zero-step Operators (h)
   - Input: list[Bar] or list[value]
   - Output: value or list[value]
   - Types:
     * Aggregation: sum, mean, median, count
     * Range: max, min
     * Comparison: diff, compare between two bars
     * Accessors: get_value(axis='x'|'y'), get_bar_info()
     * Sorting: sort(list) -> sorted list

2. One-step Operators (f) 
   - Input: list[Bar]
   - Output: filtered list[Bar]
   - Types:
     * filter(list, condition): Filter bars matching condition
     * select(position): Get bar at specific position
     * threshold(list, value, direction='above'|'below'): Filter by threshold
     * left_of(label): Get bars left of given label
   - Must be combined with zero-step operator: h(f())

3. Compositional Operators
   - Op_a(Op_b): Creates new operator that applies Op_b then Op_a
   - Op_a(Op_b, Op_c): Creates new operator that applies Op_b and Op_c, then combines with Op_a
   - Op_a(Op_b(Op_c)): Nested composition supported

4. Operation Sequence:
    - op_a(op_b(op_c)): c -> b -> a
    - op_a(op_b, op_c): (c -> b) -> a
"""

@dataclass
class OperatorResult:
    """Container for operator results with reasoning sequence."""
    value: Any
    indices: List[int]
    reasoning: List[str]
    step_indices: List[List[int]] = None  # Track indices from each operator step

    def __post_init__(self):
        if self.step_indices is None:
            self.step_indices = []

    def __repr__(self):
        return f"OperatorResult(value={self.value}, indices={self.indices}, reasoning={self.reasoning}, step_indices={self.step_indices})"

class Operator(ABC):
    """Abstract base class for bar chart operators."""
    
    def __init__(self, chart_metadata: Dict = None, config: Dict = None, random_state: int = None):
        """Initialize operator with chart metadata and configuration."""
        self.chart_metadata = chart_metadata or {}
        self.config = config or {}
        
        # Extract commonly used metadata
        self.bar_data = self.chart_metadata.get('bar_data', [])
        self.bar_labels = self.chart_metadata.get('bar_labels', [])
        self.x_label = self.chart_metadata.get('x_label', 'Category')
        self.y_label = self.chart_metadata.get('y_label', 'Value')
        self.chart_direction = self.chart_metadata.get('chart_direction', 'vertical')

        
        
        # Initialize random state
        if random_state is not None:
            self.random_state = random.Random(random_state)
        else:
            self.random_state = random.Random()
    
    @abstractmethod
    def apply(self, bar_indices: List[int] = None) -> OperatorResult:
        """Apply the operator to the specified bar indices."""
        pass
    
    def __call__(self, *args, **kwargs):
        """Enable operator composition and execution."""
        # Check if we're composing with other operators
        if args and all(isinstance(arg, Operator) for arg in args):
            return self._create_composed_operator(args)
        
        # Check if first argument is callable (nested composition)
        if args and callable(args[0]) and not isinstance(args[0], list):
            return self._create_composed_operator(args)
        
        # Otherwise, execute the operator
        if args and isinstance(args[0], list) and all(isinstance(x, int) for x in args[0]):
            # First argument is bar_indices
            bar_indices = args[0]
        else:
            # Use default indices or from kwargs
            bar_indices = kwargs.get('bar_indices', list(range(len(self.bar_data))))
        
        return self.apply(bar_indices)
    
    def _create_composed_operator(self, operators):
        """Return function: Return a new composed operator op_a(op_b), ... (a function that can be called)"""
        if len(operators) == 1:
            # Sequential composition: op_a(op_b) or op_a(op_b(op_c))
            return lambda bar_indices=None: self._apply_sequential(
                operators[0], bar_indices or list(range(len(self.bar_data)))
            )
        else:
            # Parallel composition: op_a(op_b, op_c, ...)
            return lambda bar_indices=None: self._apply_parallel(
                operators, bar_indices or list(range(len(self.bar_data)))
            )
    
    def _apply_sequential(self, op_b, bar_indices):
        """Actual execution: op_self(op_b) or op_self(op_b(op_c))"""
        # Handle nested composition
        if callable(op_b) and not isinstance(op_b, Operator):
            op_b_result = op_b(bar_indices)
        else:
            op_b_result = op_b.apply(bar_indices)
        
        # Use indices from op_b result for next operation
        if hasattr(op_b_result.value, '__iter__') and not isinstance(op_b_result.value, str):
            if all(isinstance(x, int) for x in op_b_result.value):
                next_indices = op_b_result.value
            else:
                next_indices = op_b_result.indices
        else:
            next_indices = op_b_result.indices
        
        self_result = self.apply(next_indices)
        
        # Combine reasoning and step indices
        combined_reasoning = op_b_result.reasoning + self_result.reasoning
        combined_step_indices = op_b_result.step_indices + self_result.step_indices
        return OperatorResult(self_result.value, self_result.indices, combined_reasoning, combined_step_indices)
    
    def _apply_parallel(self, operators, bar_indices):
        """Actual execution: op_self(op_b, op_c, ...)"""
        results = []
        for op in operators:
            if callable(op) and not isinstance(op, Operator): # complex like f1(f2) (returned function instead of operator)
                results.append(op(bar_indices))
            else:
                results.append(op.apply(bar_indices))
        
        # Combine results
        combined_indices = list(set(idx for r in results for idx in r.indices))
        
        # Combine reasoning and step indices
        combined_reasoning = []
        combined_step_indices = []
        for r in results:
            combined_reasoning.extend(r.reasoning)
            combined_step_indices.extend(r.step_indices)
        
        # Apply self operation
        self_result = self.apply(combined_indices)
        combined_reasoning.extend(self_result.reasoning)
        combined_step_indices.extend(self_result.step_indices)
        
        # Use self_result.indices (final result) instead of combined_indices (union of parallel inputs)
        return OperatorResult(self_result.value, self_result.indices, combined_reasoning, combined_step_indices)
