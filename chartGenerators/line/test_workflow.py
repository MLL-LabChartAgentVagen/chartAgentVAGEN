"""
Test harness for the line chart workflow.
Generates a single chart, associated QA data, and masked assets.
"""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_LINE
from chartGenerators.line.line import LineChartRunDraw
from chartGenerators.line.line_chart_generator import LineChartGenerator


class TestArgs:
    """Minimal args container for workflow smoke tests."""

    def __init__(self):
        self.chart_type = "line"
        self.chart_mode = "single"
        self.data_path = "./data"
        self.construction_subtask = "0123"
        self.global_figsize = (10, 6)
        self.gray_mask = "#CCCCCC"


def test_single_chart_workflow():
    """Run the workflow for the first metadata entry."""
    args = TestArgs()
    func_id = next(iter(METADATA_LINE.keys()))
    category_id = next(iter(METADATA_LINE[func_id].keys()))
    chart_entry = METADATA_LINE[func_id][category_id][0]

    class SingleChartRunDraw(LineChartRunDraw):
        def run_draw_single_figure(self):
            self._init_dir(self.root_path)
            chart_id = "line__img_1__test"
            chart_entry["chart_direction"] = "vertical"

            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            if "1" in self.args.construction_subtask:
                self.draw_chart_function(
                    args=self.args,
                    line_data=chart_entry["line_data"],
                    line_labels=chart_entry["line_labels"],
                    line_colors=chart_entry["line_colors"],
                    x_labels=chart_entry["x_labels"],
                    x_label=chart_entry["x_label"],
                    y_label=chart_entry["y_label"],
                    img_title=chart_entry["img_title"],
                    horizontal=False,
                    line_styles=["-", ":", "--", "-."],
                    line_widths=[3.0, 3.0, 3.0, 3.0],
                    marker_styles=["o", "^", "s", "D"],
                    show_markers=True,
                    show_text_label=True,
                    show_legend=True,
                    change_x_axis_pos=False,
                    change_y_axis_pos=False,
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )

            self.vqa_generator = LineChartGenerator(self.args, chart_id)
            qa_examples = self.vqa_generator.chart_qa_generator(chart_entry, random_seed=42, num_questions=3)

            for qa_data in qa_examples:
                qa_id = qa_data["qa_id"]
                mask_paths = {}
                for step_key in qa_data["mask"]:
                    mask_paths[step_key] = (
                        f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{qa_id}__mask_{step_key}.png"
                    )

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

                # Mask indices in QA data are the series to hide; pass through directly
                for step_key, mask_idx_list in qa_data["mask"].items():
                    mask_id = mask_paths[step_key].split("/")[-1].replace(".png", "").strip()
                    self._plot_masked_chart(
                        mask_idx_list=mask_idx_list,
                        chart_entry=chart_entry,
                        chart_direction="vertical",
                        line_styles=["-", ":", "--", "-."],
                        line_widths=[3.0, 3.0, 3.0, 3.0],
                        marker_styles=["o", "^", "s", "D"],
                        show_markers="w_markers",
                        show_label="labeled",
                        show_legend="w_legend",
                        x_axis_pos="xbottom",
                        y_axis_pos="yleft",
                        chart_id=chart_id,
                        mask_id=mask_id,
                    )

            self._save_chart_qa_data_to_json()

    runner = SingleChartRunDraw(args)
    runner.run_draw_single_figure()
    print("✅ Line chart workflow test completed.")


if __name__ == "__main__":
    test_single_chart_workflow()

