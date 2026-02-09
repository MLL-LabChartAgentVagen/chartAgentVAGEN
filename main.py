"""
Main entry point for chart generation.
Runs bar_chart and pie_chart pipelines with generated metadata JSON.
Supports: number of chart-QA sets, stages, input file, output directory, and all chart parameters.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from chartGenerators.bar_chart.main import BarChartRunDraw
from chartGenerators.pie_chart.main import PieChartRunDraw
from utils.logger import logger


def parse_stages(stages_str: str) -> str:
    """
    Parse and validate construction stages string.
    Valid stages for bar/pie: 0 (bbox images), 1 (original images).
    """
    stages_str = stages_str.replace(",", "").replace(" ", "")
    valid_stages = set("01")
    stages_set = set(stages_str)
    if not stages_set.issubset(valid_stages):
        invalid = stages_set - valid_stages
        raise ValueError(
            f"Invalid stages: {invalid}. Valid stages are: 0 (bbox images), 1 (original images)"
        )
    seen = set()
    unique = []
    for s in stages_str:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return "".join(unique)


def parse_figsize(figsize_str: str) -> tuple:
    """Parse figure size string 'width,height' into tuple."""
    parts = figsize_str.split(",")
    if len(parts) != 2:
        raise ValueError("Figure size must be in format 'width,height'")
    return (float(parts[0].strip()), float(parts[1].strip()))


def build_args_for_chart_type(
    chart_type: str,
    input_path: str,
    output_dir: str,
    num_charts: int,
    stages: str,
    num_questions: int,
    random_seed: int,
    figsize: tuple,
    gray_mask: str,
    bbox_color: str,
    composition_types: list,
) -> object:
    """Build an args object compatible with BarChartRunDraw / PieChartRunDraw."""
    class Args:
        pass
    args = Args()
    args.chart_type = chart_type
    args.chart_mode = "single"
    args.data_path = output_dir
    args.construction_subtask = stages
    args.global_figsize = figsize
    args.gray_mask = gray_mask
    args.bbox_color = bbox_color
    args.metadata_path = input_path
    args.num_charts = num_charts
    args.num_questions_per_chart = num_questions
    args.random_seed = random_seed
    args.composition_types = composition_types
    return args


def main():
    parser = argparse.ArgumentParser(
        description="Chart generation: bar and pie charts from generated metadata JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10 bar + 10 pie chart-QA sets from generated_metadata.json, original images only
  python main.py --input generated_metadata.json --output ./data --num-charts 10 --stages 1

  # Generate 5 of each type with both original and bbox images
  python main.py --input generated_metadata.json --output ./out --num-charts 5 --stages 01

  # Bar charts only, 20 chart-QA sets
  python main.py --input generated_metadata.json --chart-types bar --num-charts 20 --stages 1

  # Full options
  python main.py --input generated_metadata.json --output ./data --num-charts 10 \\
      --stages 01 --num-questions 15 --figsize 12,8

Stages:
  0: bbox images (highlighted regions)
  1: original chart images
        """
    )

    # Required / core options
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="generated_metadata.json",
        help="Input metadata JSON file (e.g. generated_metadata.json). (default: generated_metadata.json)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./data",
        help="Output directory for charts and QA data (default: ./data)"
    )
    parser.add_argument(
        "--num-charts", "-n",
        type=int,
        default=10,
        help="Number of chart-QA sets to generate per chart type (default: 10). With bar+pie this yields 2*num-charts total."
    )
    parser.add_argument(
        "--stages",
        type=str,
        default="1",
        help="Stages to run: '0'=bbox images, '1'=original images. Use '0', '1', or '01' (default: 1)"
    )
    parser.add_argument(
        "--chart-types",
        type=str,
        nargs="+",
        choices=["bar", "pie"],
        default=["bar", "pie"],
        help="Chart types to generate (default: bar pie)"
    )

    # Chart/QA parameters (forwarded to bar and pie pipelines)
    parser.add_argument(
        "--num-questions",
        type=int,
        default=20,
        help="Number of questions per chart (default: 20)"
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--figsize",
        type=str,
        default="10,6",
        help="Figure size as width,height (default: 10,6)"
    )
    parser.add_argument(
        "--gray-mask",
        type=str,
        default="#CCCCCC",
        help="Gray color for masking (default: #CCCCCC)"
    )
    parser.add_argument(
        "--bbox-color",
        type=str,
        default="#FF0000",
        help="Bounding box color (default: #FF0000)"
    )
    parser.add_argument(
        "--composition-types",
        type=str,
        nargs="+",
        choices=["one_step", "parallel", "nested"],
        default=None,
        help="QA composition types (bar only). Default: all. (one_step, parallel, nested)"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.is_file():
        logger.error(f"Input file not found: {input_path}")
        logger.error("Use --input to point to a generated metadata JSON (e.g. generated_metadata.json).")
        sys.exit(1)

    # Parse stages
    try:
        stages = parse_stages(args.stages)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Parse figsize
    try:
        figsize = parse_figsize(args.figsize)
    except ValueError as e:
        logger.error(f"Invalid --figsize: {e}")
        sys.exit(1)

    # Resolve paths
    output_dir = str(Path(args.output).resolve())
    input_abs = str(input_path.resolve())

    logger.info("=" * 80)
    logger.info("Chart Generation (Bar + Pie from generated metadata)")
    logger.info("=" * 80)
    logger.info(f"Input file:    {input_abs}")
    logger.info(f"Output dir:   {output_dir}")
    logger.info(f"Num charts:   {args.num_charts} per chart type")
    logger.info(f"Chart types:  {args.chart_types}")
    logger.info(f"Stages:       {stages} (0=bbox, 1=original)")
    logger.info(f"Num questions per chart: {args.num_questions}")
    logger.info(f"Random seed:  {args.random_seed}")
    logger.info(f"Figsize:      {figsize}")
    logger.info("=" * 80)

    chart_types = list(dict.fromkeys(args.chart_types))  # preserve order, no dupes

    for chart_type in chart_types:
        try:
            run_args = build_args_for_chart_type(
                chart_type=chart_type,
                input_path=input_abs,
                output_dir=output_dir,
                num_charts=args.num_charts,
                stages=stages,
                num_questions=args.num_questions,
                random_seed=args.random_seed,
                figsize=figsize,
                gray_mask=args.gray_mask,
                bbox_color=args.bbox_color,
                composition_types=args.composition_types,
            )
            if chart_type == "bar":
                generator = BarChartRunDraw(run_args)
            else:
                generator = PieChartRunDraw(run_args)
            logger.info(f"Running {chart_type} chart generation ({args.num_charts} chart-QA sets)...")
            generator.run_draw_single_figure()
            logger.info(f"{chart_type} chart generation completed.")
        except FileNotFoundError as e:
            logger.error(f"{chart_type}: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"{chart_type} generation failed: {e}", exc_info=True)
            sys.exit(1)

    logger.info("=" * 80)
    logger.info("All chart generation completed successfully.")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
