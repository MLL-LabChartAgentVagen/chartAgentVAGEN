import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from abc import ABC, abstractmethod
import copy

from templates.operator import Operator, OperatorResult
from templates.question_generator import QuestionGenerator


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

class Parser(ABC):
    """Abstract base class for parsers."""
    @abstractmethod
    def parse(self, settings: OperationSettings) -> ParsedOperation:
        pass
    
