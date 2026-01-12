"""Random QA generator for heatmap charts."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple
import sys
from pathlib import Path

try:
    from templates.chart_generator import ChartGenerator
    from templates.parser import OperationSettings
except ImportError:  # pragma: no cover
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from templates.chart_generator import ChartGenerator
    from templates.parser import OperationSettings

from chartGenerators.heatmap.heatmap_parser import execute_operation


class HeatmapChartGenerator(ChartGenerator):
    """Produce QA examples for heatmap charts using random compositions."""

    def __init__(self, args, chart_id: str):
        self.args = args
        self.chart_type = getattr(args, "chart_type", "heatmap")
        self.chart_id = chart_id
        self.round_num = 2
        self.qa_idx = 0
        self.random_state: Optional[random.Random] = None
        self.current_chart_metadata: Optional[Dict] = None
        self.all_qa_data_list: List[Dict] = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _format_answer(self, answer: Any) -> str:
        if isinstance(answer, float):
            return format(answer, f".{self.round_num}f")
        if isinstance(answer, list):
            return ", ".join(str(item) for item in answer)
        return str(answer)

    def _ensure_index_list(self, indices) -> List[int]:
        if indices is None:
            return []
        if isinstance(indices, (list, tuple, set)):
            result: List[int] = []
            for item in indices:
                if isinstance(item, (list, tuple, set)):
                    result.extend(self._ensure_index_list(item))
                else:
                    result.append(int(item))
            return result
        return [int(indices)]

    def _create_qa_data(
        self,
        qa_type: str,
        question: str,
        reasoning: List[str],
        answer: Any,
        mask_indices: List[int],
        constraint: Optional[str] = None,
        curriculum_level: int = 1,
        step_indices: Optional[List[List[int]]] = None,
        num_cells: Optional[int] = None,
    ) -> Dict:
        self.qa_idx += 1
        reasoning_dict = {f"step_{i + 1}": step for i, step in enumerate(reasoning)}
        normalized_mask_indices = self._ensure_index_list(mask_indices)

        if num_cells is None:
            if self.current_chart_metadata:
                rows = len(self.current_chart_metadata.get("heatmap_data", []))
                cols = len(self.current_chart_metadata.get("heatmap_data", [[]])[0]) if rows else 0
                num_cells = rows * cols
            elif normalized_mask_indices:
                num_cells = max(normalized_mask_indices) + 1
            else:
                num_cells = 0

        all_indices = list(range(num_cells))
        mask_dict: Dict[str, List[int]] = {}

        if step_indices:
            normalized_steps = [self._ensure_index_list(step) for step in step_indices]
            num_reasoning_steps = len(reasoning)
            output_indices_list: List[List[int]] = []

            if num_reasoning_steps == 1:
                output_indices_list.append(
                    normalized_steps[-1] if normalized_steps else normalized_mask_indices
                )
            elif num_reasoning_steps == 2:
                if len(normalized_steps) >= 2:
                    output_indices_list.append(normalized_steps[1])
                else:
                    output_indices_list.append(
                        normalized_steps[0] if normalized_steps else normalized_mask_indices
                    )
                output_indices_list.append(
                    normalized_steps[-1] if normalized_steps else normalized_mask_indices
                )
            else:
                num_parallel_ops = num_reasoning_steps - 1
                for i in range(num_parallel_ops):
                    output_idx = (i * 2) + 1
                    if output_idx < len(normalized_steps):
                        output_indices_list.append(normalized_steps[output_idx])
                    else:
                        fallback_idx = output_idx - 1 if output_idx > 0 else 0
                        if fallback_idx < len(normalized_steps):
                            output_indices_list.append(normalized_steps[fallback_idx])
                        else:
                            output_indices_list.append(normalized_mask_indices)
                output_indices_list.append(
                    normalized_steps[-1] if normalized_steps else normalized_mask_indices
                )

            if output_indices_list:
                output_indices_list[-1] = (
                    normalized_mask_indices if normalized_mask_indices else output_indices_list[-1]
                )
            else:
                output_indices_list.append(normalized_mask_indices)

            for i, step_reasoning in enumerate(reasoning):
                step_key = f"step_{i + 1}"
                output_indices = (
                    output_indices_list[i]
                    if i < len(output_indices_list)
                    else normalized_mask_indices
                )
                masked_indices = [idx for idx in all_indices if idx not in output_indices]
                mask_dict[step_key] = masked_indices
        else:
            masked_indices = [idx for idx in all_indices if idx not in normalized_mask_indices]
            mask_dict = {f"step_{i + 1}": masked_indices for i, _ in enumerate(reasoning)}

        answer_masked_indices = [idx for idx in all_indices if idx not in normalized_mask_indices]
        mask_dict["answer"] = answer_masked_indices

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

    # ------------------------------------------------------------------
    # Random configuration helpers
    # ------------------------------------------------------------------
    def _generate_random_configs(self, chart_metadata: Dict) -> Dict:
        flat_values = [value for row in chart_metadata["heatmap_data"] for value in row]
        min_val = min(flat_values)
        max_val = max(flat_values)
        unique_count = len(set(flat_values))
        num_cells = len(flat_values)

        if max_val == min_val:
            threshold_value = round(min_val, self.round_num)
        else:
            margin = (max_val - min_val) * 0.1
            lower = min_val + margin
            upper = max_val - margin
            if lower >= upper:
                threshold_value = round((min_val + max_val) / 2, self.round_num)
            else:
                threshold_value = round(self.random_state.uniform(lower, upper), self.round_num)

        kth_upper = unique_count if unique_count > 0 else num_cells
        kth_upper = max(1, kth_upper)

        return {
            "threshold": {
                "threshold": threshold_value,
                "direction": self.random_state.choice(["above", "below"]),
            },
            "kth": {
                "k": self.random_state.randint(1, kth_upper),
                "direction": self.random_state.choice(["highest", "lowest"]),
            },
            "topk": {
                "k": self.random_state.randint(1, min(num_cells, 5)),
                "direction": self.random_state.choice(["top", "bottom"]),
            },
        }

    def _generate_random_operator_composition(
        self, chart_metadata: Dict, complexity_level: int = 1
    ) -> Tuple[OperationSettings, str, int]:
        configs = self._generate_random_configs(chart_metadata)
        zero_ops = ["sum", "mean", "median", "count", "max", "min", "diff", "read"]
        zero_op = self.random_state.choice(zero_ops)

        if zero_op == "diff":
            op1 = OperationSettings("kth", configs["kth"])
            second_cfg = dict(configs["kth"])
            second_cfg["direction"] = (
                "lowest" if configs["kth"]["direction"] == "highest" else "highest"
            )
            op2 = OperationSettings("kth", second_cfg)
            composed = OperationSettings(zero_op, {}, args=[op1, op2])
            desc = f"parallel_{zero_op}_of_{op1.operation}_and_{op2.operation}"
            return composed, desc, 2

        if complexity_level == 1:
            if self.random_state.random() < 0.6:
                one_op = OperationSettings("all", {})
                desc = f"simple_{zero_op}"
            else:
                choice = self.random_state.choice(["threshold", "kth", "topk"])
                one_op = OperationSettings(choice, configs[choice])
                desc = f"simple_{zero_op}_of_{choice}"
            composed = OperationSettings(zero_op, {}, args=[one_op])
            return composed, desc, 1

        if complexity_level == 2:
            one_step_ops = ["threshold", "kth", "topk", "all"]
            op1_name = self.random_state.choice(one_step_ops)
            op2_name = self.random_state.choice(one_step_ops)
            op1 = OperationSettings(op1_name, configs.get(op1_name, {}))
            op2 = OperationSettings(op2_name, configs.get(op2_name, {}))
            composed = OperationSettings(zero_op, {}, args=[op1, op2])
            desc = f"parallel_{zero_op}_of_{op1_name}_and_{op2_name}"
            return composed, desc, 2

        one_step_ops = ["threshold", "kth", "topk", "all"]
        outer_name = self.random_state.choice(one_step_ops)
        inner_name = self.random_state.choice(one_step_ops)
        inner_settings = OperationSettings(inner_name, configs.get(inner_name, {}))
        outer_settings = OperationSettings(outer_name, configs.get(outer_name, {}), args=[inner_settings])
        composed = OperationSettings(zero_op, {}, args=[outer_settings])
        desc = f"nested_{zero_op}_of_{outer_name}_of_{inner_name}"
        return composed, desc, 3

    def _extract_constraint_from_settings(self, settings: OperationSettings) -> Optional[str]:
        if not settings.args:
            return None
        constraints: List[str] = []
        for arg in settings.args:
            cfg = arg.config or {}
            if arg.operation == "threshold":
                direction = cfg.get("direction", "")
                threshold = cfg.get("threshold", "")
                constraints.append(f"{direction} {threshold}")
            elif arg.operation == "kth":
                k = cfg.get("k", "")
                direction = cfg.get("direction", "")
                constraints.append(f"{k}th {direction}")
            elif arg.operation == "topk":
                k = cfg.get("k", "")
                direction = cfg.get("direction", "")
                phrase = "top" if direction == "top" else "bottom"
                constraints.append(f"{phrase} {k}")
            elif arg.operation == "all":
                constraints.append("all cells")

            child = self._extract_constraint_from_settings(arg)
            if child:
                constraints.append(child)

        if not constraints:
            return None
        return " and ".join(constraints)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_random_qa_data(
        self, chart_metadata: Dict, random_seed: int, num_questions: int = 20
    ) -> List[Dict]:
        self.random_state = random.Random(random_seed)
        self.all_qa_data_list = []
        self.qa_idx = 0
        self.current_chart_metadata = chart_metadata

        complexity_weights = [0.4, 0.4, 0.2]
        successful = 0
        rows = len(chart_metadata.get("heatmap_data", []))
        cols = len(chart_metadata.get("heatmap_data", [[]])[0]) if rows else 0
        total_cells = rows * cols

        for _ in range(num_questions * 3):
            if successful >= num_questions:
                break
            try:
                complexity = self.random_state.choices([1, 2, 3], weights=complexity_weights)[0]
                op_settings, description, curriculum_level = self._generate_random_operator_composition(
                    chart_metadata, complexity
                )
                result, question = execute_operation(op_settings, chart_metadata)
                if hasattr(result, "value"):
                    answer = result.value
                    mask_indices = self._ensure_index_list(result.indices)
                    reasoning = result.reasoning or ["I need to perform the requested operation."]
                    step_indices = getattr(result, "step_indices", None)
                else:
                    answer = result
                    mask_indices = list(range(total_cells))
                    reasoning = ["I need to perform the requested operation."]
                    step_indices = None

                constraint = self._extract_constraint_from_settings(op_settings)
                qa_data = self._create_qa_data(
                    qa_type=f"random__{description}",
                    question=question,
                    reasoning=reasoning,
                    answer=answer,
                    mask_indices=mask_indices,
                    constraint=constraint,
                    curriculum_level=curriculum_level,
                    step_indices=step_indices,
                    num_cells=total_cells,
                )
                self.all_qa_data_list.append(qa_data)
                successful += 1
            except Exception:
                continue

        return self.all_qa_data_list

    def chart_qa_generator(
        self,
        chart_metadata: Dict,
        random_seed: int = 42,
        num_questions: int = 20,
    ) -> List[Dict]:
        return self.generate_random_qa_data(chart_metadata, random_seed, num_questions)


__all__ = ["HeatmapChartGenerator"]

