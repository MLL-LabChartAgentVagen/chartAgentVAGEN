from typing import List, Dict, Any
from abc import abstractmethod
import sys
from pathlib import Path

try:
    from templates.question_generator import QuestionGenerator
except ImportError:
    # Fallback: add project root to path if package structure isn't set up
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.question_generator import QuestionGenerator


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