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
        pie_data_category = self.chart_metadata.get('pie_data_category', {"plural": "values"})
        return f"sum of all {pie_data_category.get('plural', 'values')}"


class MeanQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"plural": "values"})
        templates = [f"average of all {pie_data_category.get('plural', 'values')}", 
                     f"mean of all {pie_data_category.get('plural', 'values')}"]
        return self.random_state.choice(templates)


class MedianQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"plural": "values"})
        templates = [f"median of all {pie_data_category.get('plural', 'values')}", 
                     f"middle value of all {pie_data_category.get('plural', 'values')}"]
        return self.random_state.choice(templates)


class CountQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_label_category = self.chart_metadata.get('pie_label_category', {"plural": "categories"})
        return f"number of {pie_label_category.get('plural', 'categories')}"


class MaxQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"singular": "value"})
        templates = [f"highest {pie_data_category.get('singular', 'value')}", 
                     f"maximum {pie_data_category.get('singular', 'value')}", 
                     f"largest {pie_data_category.get('singular', 'value')}"]
        return self.random_state.choice(templates)


class MinQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"singular": "value"})
        templates = [f"lowest {pie_data_category.get('singular', 'value')}", 
                     f"minimum {pie_data_category.get('singular', 'value')}", 
                     f"smallest {pie_data_category.get('singular', 'value')}"]
        return self.random_state.choice(templates)


class DifferenceQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"plural": "values"})
        return f"difference in {pie_data_category.get('plural', 'values')}"


class ReadValueQuestionGenerator(QuestionGenerator):
    def generate_question(self):
        pie_data_category = self.chart_metadata.get('pie_data_category', {"plural": "values"})
        return f"{pie_data_category.get('plural', 'values')}"


# ============================================================
#                   One-step Question Generators (f)
# ============================================================

class ThresholdQuestionGenerator(QuestionGenerator):
    """slices (above/below) on a threshold"""
    def generate_question(self):
        threshold = self.config.get('threshold')
        direction = self.config.get('direction', 'above')
        pie_label_category = self.chart_metadata.get('pie_label_category', {"plural": "categories"})
        
        if threshold is not None:
            return f"{pie_label_category.get('plural', 'categories')} {direction} {threshold}"
        return f"{pie_label_category.get('plural', 'categories')} that meet the condition"


class KthQuestionGenerator(QuestionGenerator):
    """k-th highest/lowest slice (single slice)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'highest')
        pie_label_category = self.chart_metadata.get('pie_label_category', {"singular": "category"})
        
        ordinals = {1: "1st", 2: "2nd", 3: "3rd"}
        k_ord = ordinals.get(k, f"{k}th")
        
        return f"{k_ord} {'highest' if direction == 'highest' else 'lowest'} {pie_label_category.get('singular', 'category')}"
        
class TopkQuestionGenerator(QuestionGenerator):
    """top/bottom k slices (multiple slices)"""
    def generate_question(self):
        k = self.config.get('k', 1)
        direction = self.config.get('direction', 'top')
        pie_label_category = self.chart_metadata.get('pie_label_category', {"plural": "categories"})
        
        return f"{'top' if direction == 'top' else 'bottom'} {k} {pie_label_category.get('plural', 'categories')}"


class TakeAllQuestionGenerator(QuestionGenerator):
    """all slices"""
    def generate_question(self):
        pie_label_category = self.chart_metadata.get('pie_label_category', {"plural": "categories"})
        return f"all {pie_label_category.get('plural', 'categories')}"


# ============================================================
#                        Usage Examples
# ============================================================

if __name__ == "__main__":
    # Sample chart metadata
    sample_metadata = {
        'pie_data': [35, 25, 20, 15, 5],
        'pie_labels': ["Technology", "Healthcare", "Finance", "Education", "Others"],
        'pie_data_category': {"singular": "market share", "plural": "market shares"},
        'pie_label_category': {"singular": "sector", "plural": "sectors"},
        'img_title': "Market Share Distribution by Sector"
    }
    
    print("=== Pie Chart Question Generator Test ===")
    
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

