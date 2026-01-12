import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod
import copy

from .bar_operator import (
    Operator,
    SumOperator, MeanOperator, MedianOperator, CountOperator, ReadValueOperator,
    MaxOperator, MinOperator, DifferenceOperator, ThresholdOperator, KthOperator, TopkOperator, TakeAllOperator
)
from .bar_question_generator import (
    QuestionGenerator,
    SumQuestionGenerator, MeanQuestionGenerator, MedianQuestionGenerator, CountQuestionGenerator,
    ReadValueQuestionGenerator, MaxQuestionGenerator, MinQuestionGenerator, DifferenceQuestionGenerator,
    ThresholdQuestionGenerator, KthQuestionGenerator, TopkQuestionGenerator, TakeAllQuestionGenerator
)


@dataclass
class ParsedOperation:
    """Container for parsed operation with operator and question generator."""
    operator: Operator
    question_generator: QuestionGenerator
    description: str

@dataclass
class OperationSettings:
    """Container for operation settings."""
    operation: str
    config: Dict = field(default_factory=dict)
    args: List['OperationSettings'] = field(default_factory=list)

    def __str__(self):
        """Generate simple string representation without formatting."""
        params_str = ", ".join([f"{k}={v}" for k, v in self.config.items()]) if self.config else ""
        if not self.args:
            # Base case: just the operation name with config if present
            return f"{self.operation}(params=[{params_str}])" if params_str else f"{self.operation}()"
        
        # Recursive case: operation with arguments
        arg_strs = [str(arg) for arg in self.args]
        ops_part = ", ".join(arg_strs)
        return f"{self.operation}(params=[{params_str}], OP=[{ops_part}])"
    
    def format_tree(self, indent=0):
        """Format as a tree structure for readable display."""
        spaces = "  " * indent
        result = f"{spaces}📊 {self.operation.upper()}"
        
        # Add config if present
        if self.config:
            config_str = ", ".join(f"{k}={v}" for k, v in self.config.items())
            result += f" [{config_str}]"
        
        # Add args if present
        if self.args:
            result += "\n" + f"{spaces}├─ args:"
            for i, arg in enumerate(self.args):
                prefix = "└─" if i == len(self.args) - 1 else "├─"
                result += f"\n{spaces}│  {prefix} " + arg.format_tree(indent + 2).lstrip()
        
        return result
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "operation": self.operation,
            "config": self.config,
            "args": [arg.to_dict() for arg in self.args]
        }
    
    def __repr__(self):
        """Compact representation."""
        config_str = f", config={self.config}" if self.config else ""
        args_str = f", args={len(self.args)} items" if self.args else ""
        return f"OperationSettings('{self.operation}'{config_str}{args_str})"


class BarChartParser:
    """Parser for bar chart operations and questions."""
    
    # Simplified mapping - one key per operator
    OPERATION_MAP = {
        'sum': (SumOperator, SumQuestionGenerator),
        'mean': (MeanOperator, MeanQuestionGenerator),
        'median': (MedianOperator, MedianQuestionGenerator),
        'count': (CountOperator, CountQuestionGenerator),
        'read': (ReadValueOperator, ReadValueQuestionGenerator),
        'max': (MaxOperator, MaxQuestionGenerator),
        'min': (MinOperator, MinQuestionGenerator),
        'diff': (DifferenceOperator, DifferenceQuestionGenerator),
        'threshold': (ThresholdOperator, ThresholdQuestionGenerator),
        'kth': (KthOperator, KthQuestionGenerator),
        'topk': (TopkOperator, TopkQuestionGenerator),
        'all': (TakeAllOperator, TakeAllQuestionGenerator),
    }
    
    def __init__(self, chart_metadata: Dict):
        """Initialize parser with chart metadata."""
        self.chart_metadata = chart_metadata
    
    def parse(self, settings: OperationSettings) -> ParsedOperation:
        """Parse operation settings and return operator and question generator."""
        operation = settings.operation.lower()
        
        if operation not in self.OPERATION_MAP:
            raise ValueError(f"Unknown operation: {operation}")
        
        op_class, gen_class = self.OPERATION_MAP[operation]
        
        # Create base operator and generator
        operator = op_class(self.chart_metadata, settings.config)
        generator = gen_class(self.chart_metadata, settings.config)
        
        # Handle composition if args are provided
        if settings.args:
            parsed_args = [self.parse(arg) for arg in settings.args] # recursively
            
            if len(parsed_args) == 1:
                # Sequential composition: op(arg)
                composed_op = operator(parsed_args[0].operator)
                composed_gen = generator(parsed_args[0].question_generator)
                description = f"{operation}({parsed_args[0].description})"
            else:
                # Parallel composition: op(arg1, arg2, ...)
                arg_operators = [p.operator for p in parsed_args]
                arg_generators = [p.question_generator for p in parsed_args]
                composed_op = operator(*arg_operators)
                composed_gen = generator(*arg_generators)
                arg_descriptions = ", ".join([p.description for p in parsed_args])
                description = f"{operation}({arg_descriptions})"
            
            return ParsedOperation(composed_op, composed_gen, description)
        
        return ParsedOperation(operator, generator, f"{operation} operation")


# ============================================================
#                        Convenience Functions
# ============================================================

def create_operation(settings: OperationSettings, chart_metadata: Dict) -> Tuple[Operator, QuestionGenerator]:
    """Convenience function to create operator and question generator."""
    parser = BarChartParser(chart_metadata)
    parsed = parser.parse(settings)
    return parsed.operator, parsed.question_generator


def execute_operation(settings: OperationSettings, chart_metadata: Dict) -> Tuple[Any, str]:
    """Execute operation and generate question."""
    operator, generator = create_operation(settings, chart_metadata)
    
    # Execute operation
    if callable(operator):
        result = operator()
    else:
        result = operator.apply()
    
    # Generate question
    if callable(generator):
        question = generator()
    else:
        question = generator.generate_question()
    
    return result, question


# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_metadata = {
        'bar_data': [10, 25, 15, 30, 20, 35, 12, 28],
        'bar_labels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        'x_label': 'Categories',
        'y_label': 'Values'
    }
    
    print("=== Bar Chart Parser Test ===")
    print(f"Sample Data: {sample_metadata['bar_data']}")
    print()
    
    # Test 1: Simple operation
    print("--- Test 1: Simple Operation ---")
    result, question = execute_operation(OperationSettings('mean'), sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 2: Operation with config
    print("--- Test 2: Operation with Config ---")
    filter_settings = OperationSettings('threshold', {'threshold': 20, 'direction': 'above'})
    result, question = execute_operation(filter_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 3: Sequential composition
    print("--- Test 3: Sequential Composition ---")
    seq_settings = OperationSettings('sum', args=[
        OperationSettings('threshold', {'threshold': 20, 'direction': 'above'})
    ])
    result, question = execute_operation(seq_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 4: Parallel composition
    print("--- Test 4: Parallel Composition ---")
    par_settings = OperationSettings('diff', args=[
        OperationSettings('max'),
        OperationSettings('min')
    ])
    print(f"Parallel Settings: {par_settings}")
    print(f"Parallel Settings: {par_settings.format_tree()}")
    result, question = execute_operation(par_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 5: TopK operation
    print("--- Test 5: Nested Operation ---")
    topk_settings = OperationSettings('read', args=[
        OperationSettings('kth', {'k': 2, 'direction': 'highest'}, args=[
            OperationSettings('threshold', {'threshold': 20, 'direction': 'above'})
        ])
    ])
    print(f"Nested Settings: {topk_settings}")
    print(f"Nested Settings: {topk_settings.format_tree()}")
    result, question = execute_operation(topk_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    print("=== Test Complete ===") 