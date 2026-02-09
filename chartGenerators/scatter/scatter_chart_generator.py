import copy
from typing import List, Dict, Any, Optional, Tuple
import random
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use absolute import after sys.path is set
from chartGenerators.scatter.scatter_parser import OperationSettings, execute_operation

from templates.chart_generator import ChartGenerator

# Import questions metadata
try:
    from metadata.questions_metadata import get_questions_for_chart, has_questions_for_chart
except ImportError:
    # Fallback if questions_metadata doesn't exist
    def get_questions_for_chart(*args, **kwargs):
        return []
    def has_questions_for_chart(*args, **kwargs):
        return False

class ScatterChartGenerator(ChartGenerator):
    """ScatterChartGenerator with random operator composition."""
    
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
                       curriculum_level: int = 1, step_indices: List[List[int]] = None,
                       num_scatter_points: int = None):
        """Create a single QA data entry."""
        self.qa_idx += 1
        
        # Create reasoning dict and mask
        reasoning_dict = {f"step_{i+1}": step for i, step in enumerate(reasoning)}
        
        # Get total number of scatter points for mask inversion
        if num_scatter_points is None:
            # Try to infer from mask_indices (should contain all indices if not filtered)
            num_scatter_points = max(mask_indices) + 1 if mask_indices else 10
        all_indices = list(range(num_scatter_points))
        
        # Use step_indices if provided, otherwise use mask_indices for all steps
        if step_indices:
            bbox_dict = {}
            # Extract output indices for each reasoning step
            # step_indices structure:
            # Sequential: [op1_input, op1_output, op2_input, op2_output, ...]
            # Parallel: [parallel_op1_input, parallel_op1_output, parallel_op2_input, ..., final_input, final_output]
            # Note: Some operators (like TakeAllOperator) only return [input] if output=input
            
            # Map each reasoning step to its corresponding output indices
            num_reasoning_steps = len(reasoning)
            output_indices_list = []
            
            if num_reasoning_steps == 1:
                # Single operator - use last step_indices (output)
                output_indices_list.append(step_indices[-1] if step_indices else mask_indices)
            elif num_reasoning_steps == 2:
                # Two operators (sequential or 1 parallel + final)
                # First op output at index 1, second op output at last index
                if len(step_indices) >= 2:
                    output_indices_list.append(step_indices[1])
                else:
                    output_indices_list.append(step_indices[0] if step_indices else mask_indices)
                output_indices_list.append(step_indices[-1] if step_indices else mask_indices)
            else:
                # Multiple operators (parallel composition)
                # Parallel operators: outputs at indices 1, 3, 5, ... (up to num_parallel_ops)
                # Final operator: output at last index
                num_parallel_ops = num_reasoning_steps - 1
                
                # Extract parallel operator outputs (at odd indices: 1, 3, 5, ...)
                for i in range(num_parallel_ops):
                    output_idx = (i * 2) + 1  # 1, 3, 5, ...
                    if output_idx < len(step_indices):
                        output_indices_list.append(step_indices[output_idx])
                    else:
                        # Fallback: use the input if output not available
                        fallback_idx = output_idx - 1 if output_idx > 0 else 0
                        output_indices_list.append(step_indices[fallback_idx] if fallback_idx < len(step_indices) else mask_indices)
                
                # Final operator's output is at the last index
                output_indices_list.append(step_indices[-1] if step_indices else mask_indices)
            
            # Now map reasoning steps to their output indices for bounding boxes
            for i, step_reasoning in enumerate(reasoning):
                step_key = f"step_{i+1}"
                if i < len(output_indices_list):
                    output_indices = output_indices_list[i]
                else:
                    output_indices = mask_indices
                
                # Use indices directly for bounding boxes (highlight relevant points)
                bbox_dict[step_key] = output_indices
            
            # Answer bbox: use indices directly
            bbox_dict["answer"] = mask_indices
        else:
            # Use indices directly for bounding boxes
            bbox_dict = {f"step_{i+1}": mask_indices for i, step in enumerate(reasoning)}
            bbox_dict["answer"] = mask_indices
        
        return {
            "qa_id": f"{self.chart_id}_qa{self.qa_idx}",
            "qa_type": qa_type,
            "curriculum_level": str(curriculum_level),
            "constraint": constraint,
            "question": question,
            "reasoning": reasoning_dict,
            "answer": self._format_answer(answer),
            "bbox": bbox_dict,  # Changed from "mask" to "bbox"
        }
    
    def _generate_random_configs(self, chart_metadata: Dict) -> Dict:
        """Generate random configurations for operators."""
        x_values = chart_metadata["scatter_x_data"]
        y_values = chart_metadata["scatter_y_data"]
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        unique_count_x = len(set(x_values))
        unique_count_y = len(set(y_values))
        num_points = len(x_values)
        
        # Randomly choose axis
        axis = self.random_state.choice(["x", "y"])
        values = x_values if axis == "x" else y_values
        min_val, max_val = (min_x, max_x) if axis == "x" else (min_y, max_y)
        unique_count = unique_count_x if axis == "x" else unique_count_y
        
        return {
            'axis': axis,
            'threshold': {
                'threshold': round(self.random_state.uniform(min_val + 0.1, max_val - 0.1), 1),
                'direction': self.random_state.choice(["above", "below"]),
                'axis': axis
            },
            'kth': {
                'k': self.random_state.randint(1, min(unique_count, 5)),
                'direction': self.random_state.choice(["highest", "lowest"]),
                'axis': axis
            },
            'topk': {
                'k': self.random_state.randint(1, min(num_points - 1, 3)),
                'direction': self.random_state.choice(["top", "bottom"]),
                'axis': axis
            }
        }
    
    def _generate_random_operator_composition(self, chart_metadata: Dict, 
                                            complexity_level: int = 1) -> Tuple[OperationSettings, str, int]:
        """Generate random operator composition."""
        
        # Get random configurations
        configs = self._generate_random_configs(chart_metadata)
        axis = configs['axis']
        
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
                one_op_config = configs[one_step_name].copy()
                one_op = OperationSettings(one_step_name, one_op_config)
                desc = f"simple_{zero_op}_of_{one_step_name}"
            
            # Add axis to zero-step config
            zero_op_config = {"axis": axis}
            composed = OperationSettings(zero_op, zero_op_config, args=[one_op])
            return composed, desc, 1
        
        elif complexity_level == 2:
            # Parallel: zero_step(one_step1, one_step2)
            if zero_op == "diff":
                # Diff needs exactly 2 single-value operations
                one_op1 = OperationSettings("kth", configs['kth'])
                kth_config2 = configs['kth'].copy()
                kth_config2['k'] = self.random_state.randint(1, min(len(set(chart_metadata["scatter_x_data"] if axis == "x" else chart_metadata["scatter_y_data"])), 5))
                one_op2 = OperationSettings("kth", kth_config2)
            else:
                # For sum, mean, count - use any operations
                one_step_ops = ["threshold", "kth", "topk", "all"]
                op1_name = self.random_state.choice(one_step_ops)
                op2_name = self.random_state.choice(one_step_ops)
                
                one_op1_config = configs.get(op1_name, {}).copy() if op1_name in configs else {}
                one_op2_config = configs.get(op2_name, {}).copy() if op2_name in configs else {}
                one_op1 = OperationSettings(op1_name, one_op1_config)
                one_op2 = OperationSettings(op2_name, one_op2_config)
            
            # Add axis to zero-step config
            zero_op_config = {"axis": axis}
            composed = OperationSettings(zero_op, zero_op_config, args=[one_op1, one_op2])
            desc = f"parallel_{zero_op}_of_{one_op1.operation}_and_{one_op2.operation}"
            return composed, desc, 2
        
        else:  # complexity_level == 3
            # Nested: zero_step(one_step1(one_step2))
            one_step_ops = ["threshold", "kth", "topk", "all"]
            outer_op = self.random_state.choice(one_step_ops)
            inner_op = self.random_state.choice(one_step_ops)
            
            inner_config = configs.get(inner_op, {}).copy() if inner_op in configs else {}
            outer_config = configs.get(outer_op, {}).copy() if outer_op in configs else {}
            inner_settings = OperationSettings(inner_op, inner_config)
            outer_settings = OperationSettings(outer_op, outer_config, args=[inner_settings])
            
            # Add axis to zero-step config
            zero_op_config = {"axis": axis}
            composed = OperationSettings(zero_op, zero_op_config, args=[outer_settings])
            
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
                    mask_indices = result.indices or list(range(len(chart_metadata["scatter_x_data"])))
                    reasoning = result.reasoning or ["I need to perform the requested operation."]
                    step_indices = getattr(result, 'step_indices', None)
                else:
                    answer = result
                    mask_indices = list(range(len(chart_metadata["scatter_x_data"])))
                    reasoning = ["I need to perform the requested operation."]
                    step_indices = None
                
                # Create QA data
                constraint = self._extract_constraint_from_settings(operation_settings)
                num_scatter_points = len(chart_metadata["scatter_x_data"])
                qa_data = self._create_qa_data(
                    qa_type=f"random__{description}",
                    question=question,
                    reasoning=reasoning,
                    answer=answer,
                    mask_indices=mask_indices,
                    constraint=constraint,
                    curriculum_level=curriculum_level,
                    step_indices=step_indices,
                    num_scatter_points=num_scatter_points
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
                axis = arg.config.get("axis", "x")
                axis_label = "x" if axis == "x" else "y"
                constraints.append(f"{axis_label} {direction} {threshold}")
            elif arg.operation == "kth":
                k = arg.config.get("k", "")
                direction = arg.config.get("direction", "")
                axis = arg.config.get("axis", "x")
                axis_label = "x" if axis == "x" else "y"
                constraints.append(f"{axis_label} {k}th {direction}")
            elif arg.operation == "topk":
                k = arg.config.get("k", "")
                direction = arg.config.get("direction", "")
                axis = arg.config.get("axis", "x")
                axis_label = "x" if axis == "x" else "y"
                constraints.append(f"{axis_label} {'top' if direction == 'top' else 'bottom'} {k}")
            elif arg.operation == "all":
                constraints.append("all items")
        
        return " and ".join(constraints) if constraints else None
    
    def _load_hardcoded_questions(self, chart_metadata: Dict, func_id: str, 
                                  category: str, chart_index: int = 0) -> List[Dict]:
        """
        Load and process hardcoded questions from questions_metadata.py.
        
        Args:
            chart_metadata: Chart metadata dictionary
            func_id: Function ID (e.g., "draw__3_scatter__func_1")
            category: Category name (e.g., "1 - Media & Entertainment")
            chart_index: Index of chart within category
        
        Returns:
            List of QA data dictionaries
        """
        hardcoded_questions = get_questions_for_chart(func_id, category, chart_index)
        
        if not hardcoded_questions:
            return []
        
        qa_data_list = []
        num_scatter_points = len(chart_metadata.get("scatter_x_data", []))
        all_indices = list(range(num_scatter_points))
        
        for question_template in hardcoded_questions:
            qa_type = question_template.get("qa_type", "hardcoded")
            questions = question_template.get("question", [])
            reasoning_templates = question_template.get("reasoning", [])
            constraint = question_template.get("constraint")
            answer = question_template.get("answer")
            bbox_template = question_template.get("bbox", question_template.get("mask", {}))  # Support both for backward compatibility
            
            # Compute answer if None (from chart metadata)
            if answer is None:
                # Try to infer from qa_type or compute from metadata
                answer = self._compute_answer_from_type(qa_type, chart_metadata)
            
            # Format answer
            if isinstance(answer, float):
                answer = format(answer, f'.{self.round_num}f')
            elif answer is not None:
                answer = str(answer)
            else:
                answer = "N/A"
            
            # Process each question variant with each reasoning variant
            for question_text in questions:
                for reasoning_dict in reasoning_templates:
                    self.qa_idx += 1
                    
                    # Process bbox - use indices directly (not inverted)
                    bbox_dict = {}
                    for step_key in reasoning_dict.keys():
                        if step_key in bbox_template:
                            bbox_indices = bbox_template[step_key]
                            if bbox_indices is None:
                                # Default to all indices
                                bbox_indices = all_indices
                            # Use indices directly for bounding boxes (highlight relevant points)
                            bbox_dict[step_key] = bbox_indices
                        else:
                            bbox_dict[step_key] = []
                    
                    # Answer bbox
                    if "answer" in bbox_template:
                        answer_bbox_indices = bbox_template["answer"]
                        if answer_bbox_indices is None:
                            answer_bbox_indices = all_indices
                        bbox_dict["answer"] = answer_bbox_indices
                    else:
                        bbox_dict["answer"] = []
                    
                    qa_data = {
                        "qa_id": f"{self.chart_id}_qa{self.qa_idx}",
                        "qa_type": qa_type,
                        "curriculum_level": str(1),  # Default, can be enhanced
                        "constraint": constraint,
                        "question": question_text,
                        "reasoning": reasoning_dict,
                        "answer": answer,
                        "bbox": bbox_dict,  # Changed from "mask" to "bbox"
                    }
                    
                    qa_data_list.append(qa_data)
        
        return qa_data_list
    
    def _compute_answer_from_type(self, qa_type: str, chart_metadata: Dict) -> Any:
        """
        Compute answer from qa_type if answer is None in hardcoded questions.
        
        Args:
            qa_type: Question type (e.g., "one_step__statistics__sum_x")
            chart_metadata: Chart metadata
        
        Returns:
            Computed answer value
        """
        if "sum_x" in qa_type:
            return sum(chart_metadata.get("scatter_x_data", []))
        elif "sum_y" in qa_type:
            return sum(chart_metadata.get("scatter_y_data", []))
        elif "mean_x" in qa_type or "average_x" in qa_type:
            data = chart_metadata.get("scatter_x_data", [])
            return sum(data) / len(data) if data else 0
        elif "mean_y" in qa_type or "average_y" in qa_type:
            data = chart_metadata.get("scatter_y_data", [])
            return sum(data) / len(data) if data else 0
        elif "max_x" in qa_type:
            return max(chart_metadata.get("scatter_x_data", [])) if chart_metadata.get("scatter_x_data") else None
        elif "max_y" in qa_type:
            return max(chart_metadata.get("scatter_y_data", [])) if chart_metadata.get("scatter_y_data") else None
        elif "min_x" in qa_type:
            return min(chart_metadata.get("scatter_x_data", [])) if chart_metadata.get("scatter_x_data") else None
        elif "min_y" in qa_type:
            return min(chart_metadata.get("scatter_y_data", [])) if chart_metadata.get("scatter_y_data") else None
        elif "count" in qa_type:
            return len(chart_metadata.get("scatter_x_data", []))
        else:
            return None
    
    def chart_qa_generator(self, chart_metadata: Dict, random_seed: int = 42, 
                          num_questions: int = 20, func_id: str = None, 
                          category: str = None, chart_index: int = 0,
                          use_hardcoded: bool = True, use_random: bool = True) -> List[Dict]:
        """
        Main interface - generate QA data from both hardcoded and random sources.
        
        Args:
            chart_metadata: Chart metadata dictionary
            random_seed: Random seed for reproducibility
            num_questions: Number of random questions to generate (if use_random=True)
            func_id: Function ID for hardcoded questions (e.g., "draw__3_scatter__func_1")
            category: Category name for hardcoded questions (e.g., "1 - Media & Entertainment")
            chart_index: Index of chart within category
            use_hardcoded: Whether to include hardcoded questions (default: True)
            use_random: Whether to include random questions (default: True)
        
        Returns:
            List of QA data dictionaries
        """
        self.all_qa_data_list = []
        self.qa_idx = 0
        
        # Load hardcoded questions if requested
        if use_hardcoded and func_id and category:
            hardcoded_qa = self._load_hardcoded_questions(
                chart_metadata, func_id, category, chart_index
            )
            self.all_qa_data_list.extend(hardcoded_qa)
        
        # Generate random questions if requested
        if use_random:
            random_qa = self.generate_random_qa_data(chart_metadata, random_seed, num_questions)
            self.all_qa_data_list.extend(random_qa)
        
        return self.all_qa_data_list

if __name__ == "__main__":
    def run_tests():
        """Run simple test cases to verify the generator works correctly."""
        
        class MockArgs:
            def __init__(self):
                self.chart_type = "scatter"
        
        # Test data
        chart_metadata = {
            'scatter_x_data': [1.2, 2.5, 3.8, 4.1, 5.3],
            'scatter_y_data': [22.75, 32.43, 33.96, 45.36, 19.32],
            'scatter_labels': ["A", "B", "C", "D", "E"],
            'x_label': 'Rating Score',
            'y_label': 'Box Office Earnings',
        }
        
        print("🧪 Running ScatterChartGenerator Tests")
        print("=" * 40)
        
        # Test 1: Basic generation
        generator = ScatterChartGenerator(MockArgs(), "test_chart")
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

