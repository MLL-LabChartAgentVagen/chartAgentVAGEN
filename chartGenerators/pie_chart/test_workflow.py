"""
Test script to generate one example from the pie chart workflow.
This demonstrates the complete pipeline: original chart, QA data, masked charts, and masks.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from metadata.metadata import METADATA_PIE
from chartGenerators.pie_chart.pie import PieChartRunDraw
from chartGenerators.pie_chart.pie_chart_generator import PieChartGenerator
from utils.logger import logger


class TestArgs:
    """Minimal args object for testing."""

    def __init__(self):
        self.chart_type = "pie"
        self.chart_mode = "single"
        self.data_path = "./data"
        # Run all stages: 0=masked images, 1=original images, 2/3=masks
        self.construction_subtask = "0123"
        self.global_figsize = (10, 6)
        self.gray_mask = "#CCCCCC"


def test_single_chart_workflow():
    """Test the complete workflow with one chart example."""

    print("=" * 100)
    print("Testing Pie Chart Workflow - Single Example")
    print("=" * 100)

    # Create test args
    args = TestArgs()

    # Get first example from metadata
    func_id = list(METADATA_PIE.keys())[0]
    category_id = list(METADATA_PIE[func_id].keys())[0]
    chart_entry = METADATA_PIE[func_id][category_id][0]  # First chart in first category

    print(f"\n📊 Chart Information:")
    print(f"  Function ID: {func_id}")
    print(f"  Category: {category_id}")
    print(f"  Chart Title: {chart_entry['img_title']}")
    print(f"  Number of slices: {len(chart_entry['pie_data'])}")
    print()

    # Create a modified RunDraw class that processes only one chart
    class SingleChartRunDraw(PieChartRunDraw):
        """Modified RunDraw that processes only one chart for testing."""

        def run_draw_single_figure(self):
            """Process only one chart example."""
            self._init_dir(self.root_path)
            self.total_img_num = 0
            self.total_vqa_num = 0
            chart_idx = 1

            # Get the first function and category
            func_id = list(METADATA_PIE.keys())[0]
            category_id = list(METADATA_PIE[func_id].keys())[0]
            chart_entry = METADATA_PIE[func_id][category_id][0]

            self.draw_chart_function = self.function_dict[func_id]["original_img"]
            self.draw_masked_chart_function = self.function_dict[func_id]["masked_img"]

            # Use representative settings for simplicity
            show_percentages = "w_percent"
            show_values = "w_value"
            show_legend = "w_legend"
            explode_slice_idx = 0
            start_angle = 45

            chart_id = (
                f"{self.args.chart_type}__img_{chart_idx}__category{category_id.split(' ')[0]}"
                f"__{show_percentages}__{show_values}__{show_legend}"
                f"__segment{explode_slice_idx}__angle{start_angle}"
            )
            chart_entry["chart_direction"] = "circular"
            explode_slices = [0 for _ in range(len(chart_entry["pie_data"]))]
            if explode_slices:
                explode_slices[explode_slice_idx] = 0.1

            print(f"\n🎨 Generating Chart: {chart_id}")
            print(f"  Show Percentages: {show_percentages}")
            print(f"  Show Values: {show_values}")
            print(f"  Show Legend: {show_legend}")
            print(f"  Exploded Slice Index: {explode_slice_idx}")
            print(f"  Start Angle: {start_angle}°")

            # Subtask 1: Original chart
            if "1" in self.args.construction_subtask:
                print(f"\n✅ Step 1: Generating original chart...")
                self.draw_chart_function(
                    args=self.args,
                    pie_data=chart_entry["pie_data"],
                    pie_labels=chart_entry["pie_labels"],
                    pie_colors=chart_entry["pie_colors"],
                    img_title=chart_entry["img_title"],
                    show_percentages=show_percentages == "w_percent",
                    show_values=show_values == "w_value",
                    show_legend=show_legend == "w_legend",
                    explode_slices=explode_slices,
                    img_save_name=f"{self.root_path}/{chart_id}.png",
                )
                print(f"  ✓ Saved: {self.root_path}/{chart_id}.png")

            # Init chart QA data generator
            print(f"\n📝 Step 2: Generating QA data...")
            self.vqa_generator = PieChartGenerator(self.args, chart_id)

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

                # Mask paths
                new_mask_path = {}
                for step_key in new_qa_data["mask"]:
                    new_mask_path[step_key] = (
                        f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{new_qa_id}__mask_{step_key}.png"
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
                    "eval_mode": show_percentages,
                    "img_path": f"./data/imgs/{self.args.chart_type}/{self.args.chart_mode}/{chart_id}.png",
                    "mask_path": new_mask_path,
                    "mask_indices": new_qa_data["mask"],
                    "question": new_qa_data["question"],
                    "reasoning": new_qa_data["reasoning"],
                    "answer": new_qa_data["answer"],
                }

                # Generate masked chart
                print(f"     Generating masked charts and masks...")
                for step_key in new_mask_path:
                    curr_mask_id = (
                        new_mask_path[step_key].split("/")[-1].replace(".png", "").strip()
                    )
                    self._plot_masked_chart(
                        mask_idx_list=new_qa_data["mask"][step_key],
                        chart_entry=chart_entry,
                        show_percentages=show_percentages,
                        show_values=show_values,
                        show_legend=show_legend,
                        explode_slices=explode_slices,
                        chart_id=chart_id,
                        mask_id=curr_mask_id,
                    )
                    print(f"       ✓ {step_key}: {curr_mask_id}")

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
    print(f"   - Original chart: {args.data_path}/imgs/{args.chart_type}/{args.chart_mode}/pie__img_1__*.png")
    print(f"   - Masked charts: {args.data_path}/imgs/{args.chart_type}/{args.chart_mode}/*__gray_mask.png")
    print(f"   - Mask files: {args.data_path}/imgs/{args.chart_type}/{args.chart_mode}/*__mask_*.png")
    print(f"   - QA data: {args.data_path}/pie__meta_qa_data.json")
    logger.info("Pie chart workflow test run complete.")


if __name__ == "__main__":
    test_single_chart_workflow()


