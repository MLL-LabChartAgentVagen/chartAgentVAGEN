"""Parser binding heatmap operators and question generators."""

from __future__ import annotations

from typing import Any, Dict, Tuple
import sys
from pathlib import Path

try:
    from templates.parser import Parser, ParsedOperation, OperationSettings
    from templates.operator import Operator
    from templates.question_generator import QuestionGenerator
except ImportError:  # pragma: no cover
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.parser import Parser, ParsedOperation, OperationSettings
    from templates.operator import Operator
    from templates.question_generator import QuestionGenerator

from chartGenerators.heatmap.heatmap_operator import (
    SumOperator,
    MeanOperator,
    MedianOperator,
    CountOperator,
    ReadValueOperator,
    MaxOperator,
    MinOperator,
    DifferenceOperator,
    ThresholdOperator,
    KthOperator,
    TopkOperator,
    TakeAllOperator,
)
from chartGenerators.heatmap.heatmap_question_generator import (
    SumQuestionGenerator,
    MeanQuestionGenerator,
    MedianQuestionGenerator,
    CountQuestionGenerator,
    ReadValueQuestionGenerator,
    MaxQuestionGenerator,
    MinQuestionGenerator,
    DifferenceQuestionGenerator,
    ThresholdQuestionGenerator,
    KthQuestionGenerator,
    TopkQuestionGenerator,
    TakeAllQuestionGenerator,
)


class HeatmapChartParser(Parser):
    """Parser that constructs heatmap-specific operator/question pairs."""

    OPERATION_MAP = {
        "sum": (SumOperator, SumQuestionGenerator),
        "mean": (MeanOperator, MeanQuestionGenerator),
        "median": (MedianOperator, MedianQuestionGenerator),
        "count": (CountOperator, CountQuestionGenerator),
        "read": (ReadValueOperator, ReadValueQuestionGenerator),
        "max": (MaxOperator, MaxQuestionGenerator),
        "min": (MinOperator, MinQuestionGenerator),
        "diff": (DifferenceOperator, DifferenceQuestionGenerator),
        "threshold": (ThresholdOperator, ThresholdQuestionGenerator),
        "kth": (KthOperator, KthQuestionGenerator),
        "topk": (TopkOperator, TopkQuestionGenerator),
        "all": (TakeAllOperator, TakeAllQuestionGenerator),
    }

    def __init__(self, chart_metadata: Dict):
        self.chart_metadata = chart_metadata

    def parse(self, settings: OperationSettings) -> ParsedOperation:
        operation = settings.operation.lower()
        if operation not in self.OPERATION_MAP:
            raise ValueError(f"Unknown operation: {operation}")

        operator_cls, generator_cls = self.OPERATION_MAP[operation]
        operator = operator_cls(self.chart_metadata, settings.config)
        generator = generator_cls(self.chart_metadata, settings.config)

        if settings.args:
            parsed_args = [self.parse(arg) for arg in settings.args]
            if len(parsed_args) == 1:
                composed_operator = operator(parsed_args[0].operator)
                composed_generator = generator(parsed_args[0].question_generator)
                description = f"{operation}({parsed_args[0].description})"
            else:
                arg_ops = [arg.operator for arg in parsed_args]
                arg_gens = [arg.question_generator for arg in parsed_args]
                composed_operator = operator(*arg_ops)
                composed_generator = generator(*arg_gens)
                arg_descriptions = ", ".join(arg.description for arg in parsed_args)
                description = f"{operation}({arg_descriptions})"
            return ParsedOperation(composed_operator, composed_generator, description)

        return ParsedOperation(operator, generator, f"{operation} operation")


def create_operation(settings: OperationSettings, chart_metadata: Dict) -> Tuple[Operator, QuestionGenerator]:
    parser = HeatmapChartParser(chart_metadata)
    parsed = parser.parse(settings)
    return parsed.operator, parsed.question_generator


def execute_operation(settings: OperationSettings, chart_metadata: Dict) -> Tuple[Any, str]:
    operator, generator = create_operation(settings, chart_metadata)
    result = operator() if callable(operator) else operator.apply()
    question = generator() if callable(generator) else generator.generate_question()
    return result, question


__all__ = [
    "HeatmapChartParser",
    "create_operation",
    "execute_operation",
]


