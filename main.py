"""
Main entry point for chart generation.
Supports multiple chart types and configurable generation stages.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from chartGenerators.bar_chart.main import BarChartRunDraw
from chartGenerators.pie_chart.pie import PieChartRunDraw
from utils.logger import logger


class ChartGenerationArgs:
    """Configuration object for chart generation."""
    
    def __init__(
        self,
        chart_type: str = "bar",
        chart_mode: str = "single",
        data_path: str = "./data",
        construction_subtask: str = "0123",
        global_figsize: tuple = (10, 6),
        gray_mask: str = "#CCCCCC"
    ):
        """
        Args:
            chart_type: Type of chart ('bar', 'pie', etc.)
            chart_mode: Mode of chart generation ('single', etc.)
            data_path: Base path for saving generated data
            construction_subtask: Stages to run ('0'=masked images, '1'=original images, '2'/'3'=masks)
            global_figsize: Figure size tuple (width, height)
            gray_mask: Gray color code for masking
        """
        self.chart_type = chart_type
        self.chart_mode = chart_mode
        self.data_path = data_path
        self.construction_subtask = construction_subtask
        self.global_figsize = global_figsize
        self.gray_mask = gray_mask


def get_chart_generator(chart_type: str, args):
    """
    Factory function to get the appropriate chart generator.
    
    Args:
        chart_type: Type of chart ('bar', 'pie', etc.)
        args: ChartGenerationArgs object
        
    Returns:
        Chart generator instance
        
    Raises:
        ValueError: If chart_type is not supported
    """
    chart_type = chart_type.lower()
    
    if chart_type == "bar":
        return BarChartRunDraw(args)
    elif chart_type == "pie":
        return PieChartRunDraw(args)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}. Supported types: 'bar', 'pie'")


def parse_stages(stages_str: str) -> str:
    """
    Parse and validate construction stages string.
    
    Args:
        stages_str: Comma-separated or concatenated stage numbers (e.g., "0,1,2,3" or "0123")
        
    Returns:
        Validated stage string (e.g., "0123")
        
    Raises:
        ValueError: If invalid stages are provided
    """
    # Remove commas and whitespace
    stages_str = stages_str.replace(",", "").replace(" ", "")
    
    # Validate that all characters are digits 0-3
    valid_stages = set("0123")
    stages_set = set(stages_str)
    
    if not stages_set.issubset(valid_stages):
        invalid = stages_set - valid_stages
        raise ValueError(
            f"Invalid stages: {invalid}. Valid stages are: 0 (masked images), "
            f"1 (original images), 2/3 (mask generation)"
        )
    
    # Remove duplicates while preserving order
    seen = set()
    unique_stages = []
    for stage in stages_str:
        if stage not in seen:
            seen.add(stage)
            unique_stages.append(stage)
    
    return "".join(unique_stages)


def main():
    """Main entry point for chart generation."""
    
    parser = argparse.ArgumentParser(
        description="Chart Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with all stages for bar charts (default)
  python main.py
  
  # Run only original image generation (stage 1)
  python main.py --stages 1
  
  # Run original and masked images (stages 0 and 1)
  python main.py --stages 0,1
  
  # Run for pie charts (when implemented)
  python main.py --chart-type pie
  
  # Custom data path
  python main.py --data-path ./custom_data

Stages:
  0: Generate masked chart images
  1: Generate original chart images  
  2/3: Generate mask files
        """
    )
    
    parser.add_argument(
        "--chart-type",
        type=str,
        default="bar",
        choices=["bar", "pie"],
        help="Type of chart to generate (default: bar)"
    )
    
    parser.add_argument(
        "--stages",
        type=str,
        default="0123",
        help="Comma-separated or concatenated stage numbers to run (default: 0123 = all stages). "
             "Valid stages: 0 (masked images), 1 (original images), 2/3 (mask generation)"
    )
    
    parser.add_argument(
        "--data-path",
        type=str,
        default="./data",
        help="Base path for saving generated data (default: ./data)"
    )
    
    parser.add_argument(
        "--chart-mode",
        type=str,
        default="single",
        help="Mode of chart generation (default: single)"
    )
    
    parser.add_argument(
        "--figsize",
        type=str,
        default="10,6",
        help="Figure size as 'width,height' (default: 10,6)"
    )
    
    parser.add_argument(
        "--gray-mask",
        type=str,
        default="#CCCCCC",
        help="Gray color code for masking (default: #CCCCCC)"
    )
    
    args = parser.parse_args()
    
    # Parse and validate stages
    try:
        construction_subtask = parse_stages(args.stages)
    except ValueError as e:
        logger.error(f"Invalid stages: {e}")
        sys.exit(1)
    
    # Parse figure size
    try:
        figsize_parts = args.figsize.split(",")
        if len(figsize_parts) != 2:
            raise ValueError("Figure size must be in format 'width,height'")
        global_figsize = (float(figsize_parts[0]), float(figsize_parts[1]))
    except (ValueError, IndexError) as e:
        logger.error(f"Invalid figure size format: {e}. Expected format: 'width,height'")
        sys.exit(1)
    
    # Create configuration object
    config = ChartGenerationArgs(
        chart_type=args.chart_type,
        chart_mode=args.chart_mode,
        data_path=args.data_path,
        construction_subtask=construction_subtask,
        global_figsize=global_figsize,
        gray_mask=args.gray_mask
    )
    
    # Log configuration
    logger.info("=" * 100)
    logger.info("Chart Generation Configuration")
    logger.info("=" * 100)
    logger.info(f"Chart Type: {config.chart_type}")
    logger.info(f"Chart Mode: {config.chart_mode}")
    logger.info(f"Data Path: {config.data_path}")
    logger.info(f"Stages: {config.construction_subtask}")
    logger.info(f"Figure Size: {config.global_figsize}")
    logger.info(f"Gray Mask: {config.gray_mask}")
    logger.info("=" * 100)
    
    try:
        # Get appropriate chart generator
        generator = get_chart_generator(config.chart_type, config)
        
        # Run the generation pipeline
        logger.info(f"Starting {config.chart_type} chart generation...")
        generator.run_draw_single_figure()
        
        logger.info("=" * 100)
        logger.info("Chart generation completed successfully!")
        logger.info("=" * 100)
        
    except Exception as e:
        logger.error(f"Error during chart generation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
