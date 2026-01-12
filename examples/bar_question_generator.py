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


# ============================================================
#                   Zero-step Question Generators (h)
# ============================================================

class SumQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return f"sum of {self.y_axis}"


class MeanQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        templates = [f"average {self.y_axis}", f"mean {self.y_axis}"]
        return self.random_state.choice(templates)


class MedianQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        templates = [f"median {self.y_axis}", f"middle {self.y_axis}"]
        return self.random_state.choice(templates)


class CountQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return f"number of {self.x_axis}"


class MaxQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        templates = [f"highest {self.y_axis}", f"maximum {self.y_axis}", f"largest {self.y_axis}"]
        return self.random_state.choice(templates)


class MinQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        templates = [f"lowest {self.y_axis}", f"minimum {self.y_axis}", f"smallest {self.y_axis}"]
        return self.random_state.choice(templates)


class DifferenceQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return f"difference in {self.y_axis}"


class ReadValueQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return f"{self.y_axis} value"


# ============================================================
#                   One-step Question Generators (f)
# ============================================================

class ThresholdQuestionGenerator(QuestionGenerator):
    """bars (above/below) on a threshold"""
    def generate_question(self):
        threshold = self.config.get('threshold')
        direction = self.config.get('direction', 'above')
        
        if threshold is not None:
            return f"{self.x_axis} {direction} {threshold}"
        return f"{self.x_axis} that meet the condition"


class KthQuestionGenerator(QuestionGenerator):
    """k-th highest/lowest bar (single bar)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'highest')
        
        ordinals = {1: "1st", 2: "2nd", 3: "3rd"}
        k_ord = ordinals.get(k, f"{k}th")
        
        return f"{k_ord} {'highest' if direction == 'highest' else 'lowest'} {self.x_axis}"
        
class TopkQuestionGenerator(QuestionGenerator):
    """top/bottom k bars (multiple bars)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'highest')
        
        return f"{'top' if direction == 'highest' else 'bottom'} {k} {self.x_axis}"


class TakeAllQuestionGenerator(QuestionGenerator):
    """all bars"""
    def generate_question(self):
        return f"all {self.x_axis}"


# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_metadata = {
        'x_label': 'Countries',
        'y_label': 'GDP',
        'bar_data': [10, 25, 15, 30, 20, 35, 12, 28],
        'bar_labels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    }
    
    print("=== Simplified Question Generator Test ===")
    
    # Create generators with chart metadata
    sum_gen = SumQuestionGenerator(sample_metadata)
    mean_gen = MeanQuestionGenerator(sample_metadata)
    filter_gen = ThresholdQuestionGenerator(sample_metadata, {'threshold': 20, 'direction': 'above'})
    max_gen = MaxQuestionGenerator(sample_metadata)
    min_gen = MinQuestionGenerator(sample_metadata)
    diff_gen = DifferenceQuestionGenerator(sample_metadata)
    kth_gen = KthQuestionGenerator(sample_metadata, {'k': 2, 'direction': 'highest'})
    
    print("--- Zero-step Questions (h) ---")
    print(f"Sum: {sum_gen()}")
    print(f"Mean: {mean_gen()}")
    
    print("\n--- One-step Questions (f) ---")
    print(f"Filter: {filter_gen()}")
    print(f"Kth: {kth_gen()}")
    
    print("\n--- Sequential Composition: h(f) ---")
    question1 = mean_gen(filter_gen)()
    print(f"Question: {question1}")
    
    print("\n--- Parallel Composition: h(f1, f2) ---")
    question2 = diff_gen(max_gen, min_gen)()
    print(f"Question: {question2}")
    
    print("\n--- Nested Composition: h(f1(f2)) ---")
    filter_gen2 = ThresholdQuestionGenerator(sample_metadata, {'threshold': 15, 'direction': 'above'})
    question3 = mean_gen(kth_gen(filter_gen2))()
    print(f"Question: {question3}")
    
    print("\n=== Test Complete ===") 