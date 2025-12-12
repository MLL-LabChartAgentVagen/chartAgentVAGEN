import sys
from pathlib import Path
from typing import Dict, Tuple, Any

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from templates.parser import ParsedOperation, Parser, OperationSettings
from templates.question_generator import QuestionGenerator
from templates.operator import Operator, OperatorResult

# Use absolute imports after sys.path is set
from chartGenerators.scatter.scatter_operator import (
    SumOperator, MeanOperator, MedianOperator, CountOperator, ReadValueOperator, ReadLabelOperator,
    MaxOperator, MinOperator, DifferenceOperator, ThresholdOperator, KthOperator, TopkOperator, TakeAllOperator
)
from chartGenerators.scatter.scatter_question_generator import (
    SumQuestionGenerator, MeanQuestionGenerator, MedianQuestionGenerator, CountQuestionGenerator,
    ReadValueQuestionGenerator, ReadLabelQuestionGenerator, MaxQuestionGenerator, MinQuestionGenerator, 
    DifferenceQuestionGenerator, ThresholdQuestionGenerator, KthQuestionGenerator, TopkQuestionGenerator, 
    TakeAllQuestionGenerator
)

class ScatterChartParser(Parser):
    """Parser for scatter chart operations and questions."""
    
    # Simplified mapping - one key per operator
    OPERATION_MAP = {
        'sum': (SumOperator, SumQuestionGenerator),
        'mean': (MeanOperator, MeanQuestionGenerator),
        'median': (MedianOperator, MedianQuestionGenerator),
        'count': (CountOperator, CountQuestionGenerator),
        'read': (ReadValueOperator, ReadValueQuestionGenerator),
        'read_label': (ReadLabelOperator, ReadLabelQuestionGenerator),
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
    parser = ScatterChartParser(chart_metadata)
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
        'scatter_x_data': [1.2, 2.5, 3.8, 4.1, 5.3],
        'scatter_y_data': [22.75, 32.43, 33.96, 45.36, 19.32],
        'scatter_labels': ["A", "B", "C", "D", "E"],
        'x_label': 'Rating Score',
        'y_label': 'Box Office Earnings',
    }
    
    print("=== Scatter Chart Parser Test ===")
    print(f"Sample X Data: {sample_metadata['scatter_x_data']}")
    print(f"Sample Y Data: {sample_metadata['scatter_y_data']}")
    print()
    
    # Test 1: Simple operation
    print("--- Test 1: Simple Operation ---")
    result, question = execute_operation(OperationSettings('mean', {'axis': 'x'}), sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 2: Operation with config
    print("--- Test 2: Operation with Config ---")
    filter_settings = OperationSettings('threshold', {'threshold': 3.0, 'direction': 'above', 'axis': 'x'})
    result, question = execute_operation(filter_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 3: Sequential composition
    print("--- Test 3: Sequential Composition ---")
    seq_settings = OperationSettings('sum', {'axis': 'x'}, args=[
        OperationSettings('threshold', {'threshold': 3.0, 'direction': 'above', 'axis': 'x'})
    ])
    result, question = execute_operation(seq_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    # Test 4: Read label
    print("--- Test 4: Read Label ---")
    label_settings = OperationSettings('read_label')
    result, question = execute_operation(label_settings, sample_metadata)
    print(f"Question: {question}")
    print(f"Result: {result}")
    print()
    
    print("=== Test Complete ===")

