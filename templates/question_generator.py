from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import random

"""
1. Zero-step Operator (h)
    - Template: "{h} of ..."
2. One-step Operator (f)
    - Template: "{x_axis_title} that {COND}."
    - E.g., "countries that have GDP above 10000."
3. Regular one step question (h(f))
    - Template: "what is {h} of {f}"
    - E.g., "what is sum of countries that have GDP above 10000."
4. Parallel Composition (h(f1, f2))
    - Template: "what is {h} of {f1} and {f2}"
5. Nested Composition (h(f1(f2)))
    - Template: "what is {h} of {f1} of {f2}"
"""


class QuestionGenerator(ABC):
    """Abstract base class for question generators."""
    
    def __init__(self, chart_metadata: Dict, config: Dict = None, random_state: int = None):
        self.chart_metadata = chart_metadata
        self.config = config or {}
        self.x_axis = chart_metadata.get('x_label', 'categories').lower()
        self.y_axis = chart_metadata.get('y_label', 'values').lower()
        
        # Initialize random state
        if random_state is not None:
            self.random_state = random.Random(random_state)
        else:
            self.random_state = random.Random()
    
    @abstractmethod
    def generate_question(self) -> str:
        """Generate a question fragment."""
        pass
    
    def __call__(self, *args, **kwargs):
        """Enable question generator composition."""
        if args and all(isinstance(arg, QuestionGenerator) for arg in args):
            if len(args) == 1:
                # Sequential: h(f) -> "{h} of {f}"
                return ComposedGenerator(self, args[0], composition_type="sequential")
            else:
                # Parallel: h(f1, f2) -> "{h} of {f1} and {f2}"
                return ComposedGenerator(self, args, composition_type="parallel")
        elif args and callable(args[0]):
            # Nested: h(f1(f2)) -> "{h} of {f1_composed_result}"
            return ComposedGenerator(self, args[0], composition_type="nested")
        
        # Final question generation - add "what is" here
        fragment = self.generate_question()
        return f"what is {fragment}"


class ComposedGenerator:
    """Handles composition of generators."""
    
    def __init__(self, main_gen, sub_gens, composition_type):
        self.main_gen = main_gen
        self.sub_gens = sub_gens
        self.composition_type = composition_type
    
    def __call__(self, **kwargs):
        """Generate final question with 'what is' prefix."""
        fragment = self._generate_fragment()
        return f"what is {fragment}"
    
    def _generate_fragment(self):
        """Generate question fragment without 'what is'."""
        main_fragment = self.main_gen.generate_question()
        
        if self.composition_type == "sequential":
            sub_fragment = self.sub_gens.generate_question()
            return f"{main_fragment} of {sub_fragment}"
            
        elif self.composition_type == "parallel":
            sub_fragments = [gen.generate_question() for gen in self.sub_gens]
            if len(sub_fragments) == 2:
                return f"{main_fragment} of {sub_fragments[0]} and {sub_fragments[1]}"
            else:
                return f"{main_fragment} of {', '.join(sub_fragments[:-1])} and {sub_fragments[-1]}"
                
        elif self.composition_type == "nested":
            # sub_gens is a callable that returns a composed generator
            nested_result = self.sub_gens()
            if hasattr(nested_result, '_generate_fragment'):
                sub_fragment = nested_result._generate_fragment()
            else:
                # Remove "what is " if present
                sub_fragment = nested_result[8:] if nested_result.startswith("what is ") else nested_result
            return f"{main_fragment} of {sub_fragment}"

