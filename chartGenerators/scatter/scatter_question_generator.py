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
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        return f"sum of all {axis_label}"


class MeanQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        templates = [f"average of all {axis_label}", f"mean of all {axis_label}"]
        return self.random_state.choice(templates)


class MedianQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        templates = [f"median of all {axis_label}", f"middle value of all {axis_label}"]
        return self.random_state.choice(templates)


class CountQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return "number of scatter points"


class MaxQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        templates = [f"highest {axis_label}", f"maximum {axis_label}", f"largest {axis_label}"]
        return self.random_state.choice(templates)


class MinQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        templates = [f"lowest {axis_label}", f"minimum {axis_label}", f"smallest {axis_label}"]
        return self.random_state.choice(templates)


class DifferenceQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        return f"difference in {axis_label}"


class ReadValueQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        return f"{axis_label}"


class ReadLabelQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        return "labels"


# ============================================================
#                   One-step Question Generators (f)
# ============================================================

class ThresholdQuestionGenerator(QuestionGenerator):
    """scatter points (above/below) on a threshold"""
    def generate_question(self):
        threshold = self.config.get('threshold')
        direction = self.config.get('direction', 'above')
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        if threshold is not None:
            return f"scatter points with {axis_label} {direction} {threshold}"
        return f"scatter points that meet the condition"


class KthQuestionGenerator(QuestionGenerator):
    """k-th highest/lowest scatter point (single point)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'highest')
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        ordinals = {1: "1st", 2: "2nd", 3: "3rd"}
        k_ord = ordinals.get(k, f"{k}th")
        
        return f"{k_ord} {'highest' if direction == 'highest' else 'lowest'} {axis_label}"
        
class TopkQuestionGenerator(QuestionGenerator):
    """top/bottom k scatter points (multiple points)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'top')
        axis = self.config.get("axis", "x")
        axis_label = self.chart_metadata.get('x_label', 'x-axis').lower() if axis == "x" else self.chart_metadata.get('y_label', 'y-axis').lower()
        
        return f"{'top' if direction == 'top' else 'bottom'} {k} {axis_label}"


class TakeAllQuestionGenerator(QuestionGenerator):
    """all scatter points"""
    def generate_question(self):
        return "all scatter points"


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
    
    print("=== Scatter Chart Question Generator Test ===")
    
    # Create generators with chart metadata
    sum_gen_x = SumQuestionGenerator(sample_metadata, {"axis": "x"})
    mean_gen_y = MeanQuestionGenerator(sample_metadata, {"axis": "y"})
    filter_gen = ThresholdQuestionGenerator(sample_metadata, {'threshold': 3.0, 'direction': 'above', 'axis': 'x'})
    max_gen = MaxQuestionGenerator(sample_metadata, {"axis": "x"})
    min_gen = MinQuestionGenerator(sample_metadata, {"axis": "y"})
    diff_gen = DifferenceQuestionGenerator(sample_metadata, {"axis": "x"})
    kth_gen = KthQuestionGenerator(sample_metadata, {'k': 2, 'direction': 'highest', 'axis': 'x'})
    read_label_gen = ReadLabelQuestionGenerator(sample_metadata)
    
    print("--- Zero-step Questions (h) ---")
    print(f"Sum X: {sum_gen_x()}")
    print(f"Mean Y: {mean_gen_y()}")
    print(f"Read Label: {read_label_gen()}")
    
    print("\n--- One-step Questions (f) ---")
    print(f"Filter: {filter_gen()}")
    print(f"Kth: {kth_gen()}")
    
    print("\n--- Sequential Composition: h(f) ---")
    question1 = mean_gen_y(filter_gen)()
    print(f"Question: {question1}")
    
    print("\n--- Parallel Composition: h(f1, f2) ---")
    question2 = diff_gen(max_gen, min_gen)()
    print(f"Question: {question2}")
    
    print("\n=== Test Complete ===")

