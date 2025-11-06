import copy
from typing import List, Dict, Any, Optional, Tuple
import random
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use absolute import after sys.path is set
from chartGenerators.bar_chart.bar_parser import OperationSettings, execute_operation

from templates.chart_generator import ChartGenerator

class BarChartGenerator(ChartGenerator):
    """BarChartGenerator with random operator composition."""
    
    def __init__(self, args, chart_id):
        self.chart_type = args.chart_type
        self.chart_id = chart_id
        self.all_qa_data_list = []
        self.round_num = 2
        self.qa_idx = 0
        self.random_state = None
    
    def _format_answer(self, answer):
        """Format answer to string with proper rounding for floats."""
        if isinstance(answer, float):
            return format(answer, f'.{self.round_num}f')
        if isinstance(answer, list):
            return ", ".join(str(item) for item in answer)
        return str(answer)
    
    def _create_qa_data(self, qa_type: str, question: str, reasoning: List[str], 
                       answer: Any, mask_indices: List[int], constraint: str = None,
                       curriculum_level: int = 1):
        """Create a single QA data entry."""
        self.qa_idx += 1
        
        # Create reasoning dict and mask
        reasoning_dict = {f"step_{i+1}": step for i, step in enumerate(reasoning)}
        mask_dict = {f"step_{i+1}": mask_indices for i, step in enumerate(reasoning)}
        mask_dict["answer"] = mask_indices
        
        return {
            "qa_id": f"{self.chart_id}_qa{self.qa_idx}",
            "qa_type": qa_type,
            "curriculum_level": str(curriculum_level),
            "constraint": constraint,
            "question": question,
            "reasoning": reasoning_dict,
            "answer": self._format_answer(answer),
            "mask": mask_dict,
        }
    
    def _generate_random_configs(self, chart_metadata: Dict) -> Dict:
        """Generate random configurations for operators."""
        values = chart_metadata["bar_data"]
        min_val, max_val = min(values), max(values)
        unique_count = len(set(values))
        num_bars = len(values)
        
        return {
            'threshold': {
                'threshold': round(self.random_state.uniform(min_val + 1, max_val - 1), 1),
                'direction': self.random_state.choice(["above", "below"])
            },
            'kth': {
                'k': self.random_state.randint(1, min(unique_count, 5)),
                'direction': self.random_state.choice(["highest", "lowest"])
            },
            'topk': {
                'k': self.random_state.randint(1, min(num_bars - 1, 3)),
                'direction': self.random_state.choice(["top", "bottom"])
            }
        }
    
    def _generate_random_operator_composition(self, chart_metadata: Dict, 
                                            complexity_level: int = 1) -> Tuple[OperationSettings, str, int]:
        """Generate random operator composition."""
        
        # Get random configurations
        configs = self._generate_random_configs(chart_metadata)
        
        # Zero-step operators
        zero_ops = ["sum", "mean", "median", "count", "max", "min", "read"]
        zero_op = self.random_state.choice(zero_ops)
        
        if complexity_level == 1:
            # Simple: zero_step(one_step) - always paired, default to "all"
            if self.random_state.random() < 0.7:  # 70% use "all" (TakeAll)
                one_op = OperationSettings("all")
                desc = f"simple_{zero_op}"
            else:
                # Use a specific one-step operator
                one_step_ops = ["threshold", "kth", "topk"]
                one_step_name = self.random_state.choice(one_step_ops)
                one_op = OperationSettings(one_step_name, configs[one_step_name])
                desc = f"simple_{zero_op}_of_{one_step_name}"
            
            composed = OperationSettings(zero_op, args=[one_op])
            return composed, desc, 1
        
        elif complexity_level == 2:
            # Parallel: zero_step(one_step1, one_step2)
            if zero_op == "diff":
                # Diff needs exactly 2 single-value operations
                one_op1 = OperationSettings("kth", configs['kth'])
                kth_config2 = configs['kth'].copy()
                kth_config2['k'] = self.random_state.randint(1, min(len(set(chart_metadata["bar_data"])), 5))
                one_op2 = OperationSettings("kth", kth_config2)
            else:
                # For sum, mean, count - use any operations
                one_step_ops = ["threshold", "kth", "topk", "all"]
                op1_name = self.random_state.choice(one_step_ops)
                op2_name = self.random_state.choice(one_step_ops)
                
                one_op1 = OperationSettings(op1_name, configs.get(op1_name, {}))
                one_op2 = OperationSettings(op2_name, configs.get(op2_name, {}))
            
            composed = OperationSettings(zero_op, args=[one_op1, one_op2])
            desc = f"parallel_{zero_op}_of_{one_op1.operation}_and_{one_op2.operation}"
            return composed, desc, 2
        
        else:  # complexity_level == 3
            # Nested: zero_step(one_step1(one_step2))
            one_step_ops = ["threshold", "kth", "topk", "all"]
            outer_op = self.random_state.choice(one_step_ops)
            inner_op = self.random_state.choice(one_step_ops)
            
            inner_settings = OperationSettings(inner_op, configs.get(inner_op, {}))
            outer_settings = OperationSettings(outer_op, configs.get(outer_op, {}), args=[inner_settings])
            composed = OperationSettings(zero_op, args=[outer_settings])
            
            desc = f"nested_{zero_op}_of_{outer_op}_of_{inner_op}"
            return composed, desc, 3
    
    def generate_random_qa_data(self, chart_metadata: Dict, random_seed: int, 
                               num_questions: int = 20) -> List[Dict]:
        """Generate random QA data using random operator compositions."""
        
        self.random_state = random.Random(random_seed)
        self.all_qa_data_list = []
        self.qa_idx = 0
        
        complexity_weights = [0.4, 0.4, 0.2]  # Simple, Moderate, Complex
        successful = 0
        
        for _ in range(num_questions * 3):  # Allow retries
            if successful >= num_questions:
                break
                
            try:
                # Choose complexity level
                level = self.random_state.choices([1, 2, 3], weights=complexity_weights)[0]
                
                # Generate composition
                operation_settings, description, curriculum_level = \
                    self._generate_random_operator_composition(chart_metadata, level)
                
                # Execute operation
                result, question = execute_operation(operation_settings, chart_metadata)
                
                # Validate and extract data
                if hasattr(result, 'value'):
                    answer = result.value
                    mask_indices = result.indices or list(range(len(chart_metadata["bar_data"])))
                    reasoning = result.reasoning or ["I need to perform the requested operation."]
                else:
                    answer = result
                    mask_indices = list(range(len(chart_metadata["bar_data"])))
                    reasoning = ["I need to perform the requested operation."]
                
                # Create QA data
                constraint = self._extract_constraint_from_settings(operation_settings)
                qa_data = self._create_qa_data(
                    qa_type=f"random__{description}",
                    question=question,
                    reasoning=reasoning,
                    answer=answer,
                    mask_indices=mask_indices,
                    constraint=constraint,
                    curriculum_level=curriculum_level
                )
                
                self.all_qa_data_list.append(qa_data)
                successful += 1
                
            except:
                continue  # Retry with different composition
        
        return self.all_qa_data_list
    
    def _extract_constraint_from_settings(self, settings: OperationSettings) -> Optional[str]:
        """Extract constraint description from operation settings."""
        if not settings.args:
            return None
        
        constraints = []
        for arg in settings.args:
            if arg.operation == "threshold":
                direction = arg.config.get("direction", "")
                threshold = arg.config.get("threshold", "")
                constraints.append(f"{direction} {threshold}")
            elif arg.operation == "kth":
                k = arg.config.get("k", "")
                direction = arg.config.get("direction", "")
                constraints.append(f"{k}th {direction}")
            elif arg.operation == "topk":
                k = arg.config.get("k", "")
                direction = arg.config.get("direction", "")
                constraints.append(f"top {k}" if direction == "top" else f"bottom {k}")
            elif arg.operation == "all":
                constraints.append("all items")
        
        return " and ".join(constraints) if constraints else None
    
    def chart_qa_generator(self, chart_metadata: Dict, random_seed: int = 42, 
                          num_questions: int = 20) -> List[Dict]:
        """Main interface - generate QA data with random operator compositions."""
        return self.generate_random_qa_data(chart_metadata, random_seed, num_questions)

if __name__ == "__main__":
    def run_tests():
        """Run simple test cases to verify the generator works correctly."""
        
        class MockArgs:
            def __init__(self):
                self.chart_type = "bar"
        
        # Test data
        chart_metadata = {
            'bar_data': [10, 25, 15, 30, 20],
            'bar_labels': ['A', 'B', 'C', 'D', 'E'],
            'x_label': 'Categories',
            'y_label': 'Values',
            'chart_direction': 'vertical'
        }
        
        print("🧪 Running BarChartGenerator Tests")
        print("=" * 40)
        
        # Test 1: Basic generation
        generator = BarChartGenerator(MockArgs(), "test_chart")
        qa_list = generator.chart_qa_generator(chart_metadata, random_seed=42, num_questions=8)
        
        print(f"✅ Test 1 - Basic generation: {len(qa_list)} questions generated")
        
        # Test 2: Reproducibility 
        qa_list2 = generator.chart_qa_generator(chart_metadata, random_seed=42, num_questions=8)
        same_results = all(qa1['answer'] == qa2['answer'] for qa1, qa2 in zip(qa_list, qa_list2))
        print(f"✅ Test 2 - Reproducibility: {'PASS' if same_results else 'FAIL'}")
        
        # Test 3: Diversity
        qa_list3 = generator.chart_qa_generator(chart_metadata, random_seed=999, num_questions=8)
        different_results = any(qa1['answer'] != qa3['answer'] for qa1, qa3 in zip(qa_list, qa_list3))
        print(f"✅ Test 3 - Diversity: {'PASS' if different_results else 'FAIL'}")
        
        # Test 4: Show sample outputs
        print(f"\n📝 Sample Questions:")
        for i, qa in enumerate(qa_list[:3]):
            print(f"  {i+1}. {qa['question']} → {qa['answer']}")
        
        print(f"\n📝 Question List: {qa_list[:3]}")
        print(f"\n🎯 All tests completed successfully!")
    
    run_tests()
