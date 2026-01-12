"""
Test script to generate one example from the bar chart workflow.
This demonstrates the complete pipeline: original chart, QA data, and bounding box charts.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_BAR
from chartGenerators.bar_chart.main import BarChartRunDraw
from chartGenerators.bar_chart.bar_chart_generator import BarChartGenerator
from utils.logger import logger


class TestArgs:
    """Minimal args object for testing."""

    def __init__(self):
        self.chart_type = "bar"
        self.chart_mode = "single"
        self.data_path = "./data"
        # Run all stages: 0=bbox images, 1=original images
        self.construction_subtask = "01"
        self.global_figsize = (10, 6)
        self.gray_mask = "#CCCCCC"
        self.bbox_color = "#FF0000"  # Red for bounding boxes


def test_single_chart_workflow():
    """Test the complete workflow with one chart example."""

    print("=" * 100)
    print("Testing Bar Chart Workflow - Single Example")
    print("=" * 100)

    # Create test args
    args = TestArgs()

    # Get first example from metadata
    func_id = list(METADATA_BAR.keys())[0]
    category_id = list(METADATA_BAR[func_id].keys())[0]
    chart_entry = METADATA_BAR[func_id][category_id][0]  # First chart in first category

    print(f"\n📊 Chart Information:")
    print(f"  Function ID: {func_id}")
    print(f"  Category: {category_id}")
    print(f"  Chart Title: {chart_entry['img_title']}")
    print(f"  Number of bars: {len(chart_entry['bar_data'])}")
    print(f"  X Label: {chart_entry['x_label']}")
    print(f"  Y Label: {chart_entry['y_label']}")
    print()

    # Create a modified RunDraw class that processes only one chart
    class SingleChartRunDraw(BarChartRunDraw):
        """Modified RunDraw that processes only one chart for testing."""

        def run_draw_single_figure(self):
            """Process only one chart example."""
            self._init_dir(self.root_path)
            self.total_img_num = 0
            self.total_vqa_num = 0
            chart_idx = 1

            # Get the first function and category
            func_id = list(METADATA_BAR.keys())[0]
            category_id = list(METADATA_BAR[func_id].keys())[0]
            chart_entry = METADATA_BAR[func_id][category_id][0]

            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_bbox_chart_function = self.function_dict[func_id]["bbox_img"]

            # Use representative settings for simplicity
            chart_direction = "vertical"
            show_label = "labeled"
            x_axis_pos = "xbottom"
            y_axis_pos = "yleft"
            show_legend = "w_legend"
            label_angle = 45

            chart_id = (
                f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}"
                f"__angle{label_angle}__{chart_direction}__{show_label}__{show_legend}"
                f"__{x_axis_pos}__{y_axis_pos}"
            )
            chart_entry["chart_direction"] = chart_direction

            print(f"\n🎨 Generating Chart: {chart_id}")
            print(f"  Direction: {chart_direction}")
            print(f"  Show Label: {show_label}")
            print(f"  Show Legend: {show_legend}")
            print(f"  X Axis: {x_axis_pos}, Y Axis: {y_axis_pos}")
            print(f"  Label Angle: {label_angle}°")

            # Subtask 1: Original chart
            if "1" in self.args.construction_subtask:
                print(f"\n✅ Step 1: Generating original chart...")
                self.draw_chart_function(
                    args=self.args,
                    bar_data=chart_entry["bar_data"],
                    bar_labels=chart_entry["bar_labels"],
                    bar_colors=chart_entry["bar_colors"],
                    x_label=chart_entry["x_label"],
                    y_label=chart_entry["y_label"],
                    img_title=chart_entry["img_title"],
                    label_angle=label_angle,
                    horizontal=chart_direction == "horizontal",
                    show_text_label=show_label == "labeled",
                    show_legend=show_legend == "w_legend",
                    change_x_axis_pos=x_axis_pos == "xtop",
                    change_y_axis_pos=y_axis_pos == "yright",
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )
                print(f"  ✓ Saved: {self.root_path}/{chart_id}.png")

            # Init chart QA data generator
            print(f"\n📝 Step 2: Generating QA data...")
            self.vqa_generator = BarChartGenerator(self.args, chart_id)

            # Generate QA data (limit to 3 questions for testing)
            qa_data_candidates = self.vqa_generator.chart_qa_generator(
                chart_entry, random_seed=42, num_questions=3
            )
            print(f"  ✓ Generated {len(qa_data_candidates)} QA examples")

            # Process each QA
            for qa_idx, new_qa_data in enumerate(qa_data_candidates, 1):
                new_qa_id = new_qa_data["qa_id"]

                if self._check_if_skip_existing_data(new_qa_id):
                    print(f"  ⚠ Skipping {new_qa_id} (already exists)")
                    continue

                print(f"\n  📋 QA Example {qa_idx}: {new_qa_id}")
                print(f"     Question: {new_qa_data['question']}")
                print(f"     Answer: {new_qa_data['answer']}")
                print(f"     Curriculum Level: {new_qa_data['curriculum_level']}")

                # Bbox paths
                new_bbox_path = {}
                for step_key in new_qa_data["bbox"]:
                    new_bbox_path[step_key] = (
                        f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{new_qa_id}__bbox_{step_key}.png"
                    )

                # Save to self.generated_vqa_data
                self.total_vqa_num += 1
                self.generated_vqa_data[new_qa_id] = {
                    "qa_id": new_qa_id,
                    "qa_type": new_qa_data["qa_type"],
                    "chart_type": self.args.chart_mode,
                    "category": category_id,
                    "curriculum_level": new_qa_data["curriculum_level"],
                    "constraint": new_qa_data["constraint"],
                    "eval_mode": show_label,
                    "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                    "bbox_path": new_bbox_path,
                    "bbox_indices": new_qa_data["bbox"],
                    "question": new_qa_data["question"],
                    "reasoning": new_qa_data["reasoning"],
                    "answer": new_qa_data["answer"],
                }

                # Generate bbox chart (highlighting relevant bars)
                print(f"     Generating bounding box charts...")
                for step_key in new_bbox_path:
                    curr_bbox_id = (
                        new_bbox_path[step_key].split("/")[-1].replace(".png", "").strip()
                    )
                    self._plot_bbox_chart(
                        bbox_idx_list=new_qa_data["bbox"][step_key],
                        chart_entry=chart_entry,
                        label_angle=label_angle,
                        chart_direction=chart_direction,
                        show_label=show_label,
                        show_legend=show_legend,
                        x_axis_pos=x_axis_pos,
                        y_axis_pos=y_axis_pos,
                        chart_id=chart_id,
                        bbox_id=curr_bbox_id,
                    )
                    print(f"       ✓ {step_key}: {curr_bbox_id}")

                # Save after each QA
                self._save_chart_qa_data_to_json()

            # Final summary
            self.total_img_num = chart_idx
            print(f"\n" + "=" * 100)
            print(f"✅ Workflow Complete!")
            print(f"  Total charts generated: {self.total_img_num}")
            print(f"  Total QA data generated: {self.total_vqa_num}")
            print(f"  Output directory: {self.root_path}")
            print(f"  QA data JSON: {self.generated_vqa_data_save_path}")
            print("=" * 100)

    # Run the test
    generator = SingleChartRunDraw(args)
    generator.run_draw_single_figure()

    print("\n🎉 Test completed successfully!")
    print(f"\n📁 Check the following files:")
    print(f"   - Original chart: {args.data_path}/imgs/{args.chart_type}/{args.chart_mode}/bar__img_1__*.png")
    print(f"   - Bounding box charts: {args.data_path}/imgs/{args.chart_type}/{args.chart_mode}/*__bbox_*.png")
    print(f"   - QA data: {args.data_path}/bar__meta_qa_data.json")
    logger.info("Bar chart workflow test run complete.")


if __name__ == "__main__":
    test_single_chart_workflow()


