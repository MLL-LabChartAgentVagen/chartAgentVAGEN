"""
Smoke test for the heatmap chart workflow.
"""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_HEATMAP
from chartGenerators.heatmap.heatmap import HeatmapChartRunDraw
from chartGenerators.heatmap.heatmap_chart_generator import HeatmapChartGenerator


class TestArgs:
    """Minimal args container."""

    def __init__(self):
        self.chart_type = "heatmap"
        self.chart_mode = "single"
        self.data_path = "./data"
        self.construction_subtask = "0123"
        self.global_figsize = (10, 6)
        self.gray_mask = "#CCCCCC"


def test_single_chart_workflow():
    args = TestArgs()
    func_id = next(iter(METADATA_HEATMAP.keys()))
    category_id = next(iter(METADATA_HEATMAP[func_id].keys()))
    chart_entry = METADATA_HEATMAP[func_id][category_id][0]

    class SingleChartRunDraw(HeatmapChartRunDraw):
        def run_draw_single_figure(self):
            self._init_dir(self.root_path)
            self.total_img_num = 0
            self.total_vqa_num = 0
            chart_id = "heatmap__img_1__test"

            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            if "1" in self.args.construction_subtask:
                self.draw_chart_function(
                    args=self.args,
                    heatmap_data=chart_entry["heatmap_data"],
                    x_labels=chart_entry["x_labels"],
                    y_labels=chart_entry["y_labels"],
                    x_label=chart_entry["x_label"],
                    y_label=chart_entry["y_label"],
                    img_title=chart_entry["img_title"],
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )

            self.vqa_generator = HeatmapChartGenerator(self.args, chart_id)
            qa_examples = self.vqa_generator.chart_qa_generator(chart_entry, random_seed=42, num_questions=3)

            self.generated_vqa_data = {}
            for qa_data in qa_examples:
                qa_id = qa_data["qa_id"]
                
                # Skip if already exists
                if self._check_if_skip_existing_data(qa_id):
                    continue
                
                mask_paths = {}
                for step_key in qa_data["mask"]:
                    mask_paths[step_key] = (
                        f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{qa_id}__mask_{step_key}.png"
                    )

                self.total_vqa_num += 1
                self.generated_vqa_data[qa_id] = {
                    "qa_id": qa_id,
                    "qa_type": qa_data["qa_type"],
                    "chart_type": self.args.chart_mode,
                    "category": category_id,
                    "curriculum_level": qa_data["curriculum_level"],
                    "constraint": qa_data["constraint"],
                    "eval_mode": "labeled",
                    "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                    "mask_path": mask_paths,
                    "mask_indices": qa_data["mask"],
                    "question": qa_data["question"],
                    "reasoning": qa_data["reasoning"],
                    "answer": qa_data["answer"],
                }

                # Process each mask step for this QA data
                for step_key, mask_idx_list in qa_data["mask"].items():
                    mask_id = mask_paths[step_key].split("/")[-1].replace(".png", "").strip()
                    self._plot_masked_chart(
                        mask_idx_list=mask_idx_list,  # Use mask_idx_list directly (indices to mask)
                        chart_entry=chart_entry,
                        chart_id=chart_id,
                        mask_id=mask_id,
                    )

                # Save after each QA
                self._save_chart_qa_data_to_json()

            self.total_img_num = 1
            self._save_chart_qa_data_to_json()

    runner = SingleChartRunDraw(args)
    runner.run_draw_single_figure()
    print("✅ Heatmap chart workflow test completed.")


if __name__ == "__main__":
    test_single_chart_workflow()

