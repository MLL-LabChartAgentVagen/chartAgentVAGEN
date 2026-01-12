"""
Chart QA Pipeline - Integrated Chart and QA Generation
For VLM Chart Comprehension Evaluation

Features:
1. Read metadata from generated_metadata.json
2. Generate chart images (bar, scatter, pie)
3. Generate corresponding QA data
4. Output paired evaluation data (including img_path + QA)
5. Output format is fully compatible with main.py (dictionary keyed by qa_id)

Usage:
    python chart_qa_pipeline.py
    python chart_qa_pipeline.py --limit 5 --num-questions 10
    python chart_qa_pipeline.py --chart-types bar scatter pie
"""

import json
import os
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import chart drawing functions
from chartGenerators.bar_chart.bar import draw__1_bar__func_1
from chartGenerators.scatter.run_draw import draw__3_scatter__func_1
from chartGenerators.pie_chart.pie import draw__8_pie__func_1

# Import QA generators
from chartGenerators.bar_chart.bar_chart_generator import BarChartGenerator


class PipelineConfig:
    """Pipeline configuration class"""
    def __init__(
        self,
        chart_type: str = "bar",
        global_figsize: tuple = (10, 6),
        gray_mask: str = "#CCCCCC"
    ):
        self.chart_type = chart_type
        self.global_figsize = global_figsize
        self.gray_mask = gray_mask


class ChartQAPipeline:
    """
    Chart QA Pipeline - Integrated Chart and QA Generation
    """
    
    def __init__(
        self,
        input_json: str = "generated_metadata.json",
        output_dir: str = "./data",
        num_questions: int = 20,
        random_seed: int = 42,
        chart_types: List[str] = None,
        limit: int = None,
        figsize: tuple = (10, 6),
        verbose: bool = True
    ):
        """
        Initialize Pipeline

        Args:
            input_json: Input metadata JSON file path
            output_dir: Output directory (for charts and QA data)
            num_questions: Number of questions to generate per chart
            random_seed: Random seed
            chart_types: List of supported chart types
            limit: Limit the number of entries to process
            figsize: Figure size
            verbose: Whether to display detailed information
        """
        self.input_json = input_json
        self.output_dir = output_dir
        self.num_questions = num_questions
        self.random_seed = random_seed
        self.chart_types = chart_types or ["bar"]
        self.limit = limit
        self.figsize = figsize
        self.verbose = verbose
        
        # Statistics information
        self.stats = {
            'total_entries': 0,
            'processed_entries': 0,
            'failed_entries': 0,
            'total_charts': 0,
            'total_questions': 0,
            'charts_by_type': {},
            'questions_by_type': {},
            'questions_by_level': {'1': 0, '2': 0, '3': 0}
        }
        
        # Generated data (dictionary keyed by qa_id, consistent with main.py format)
        self.evaluation_data = {}
        
        # Initialize directories
        self._init_directories()
    
    def _init_directories(self):
        """Initialize output directory structure"""
        # Main directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Chart subdirectories
        self.img_dir = os.path.join(self.output_dir, "imgs")
        os.makedirs(self.img_dir, exist_ok=True)
        
        for chart_type in ["bar", "scatter", "pie"]:
            chart_dir = os.path.join(self.img_dir, chart_type, "single")
            os.makedirs(chart_dir, exist_ok=True)
    
    def _log(self, message: str, level: str = "info"):
        """Log output"""
        if self.verbose:
            prefix = {
                "info": "  ",
                "success": "  ✓",
                "error": "  ✗",
                "warning": "  ⚠"
            }.get(level, "  ")
            print(f"{prefix} {message}")
    
    def load_metadata(self) -> List[Dict]:
        """Load metadata file"""
        try:
            with open(self.input_json, 'r', encoding='utf-8') as f:
                metadata_list = json.load(f)
            
            if self.limit:
                metadata_list = metadata_list[:self.limit]
            
            self.stats['total_entries'] = len(metadata_list)
            
            if self.verbose:
                print(f"✓ Successfully loaded {len(metadata_list)} metadata entries")
            
            return metadata_list
        except FileNotFoundError:
            print(f"✗ Error: File not found '{self.input_json}'")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: JSON format error - {e}")
            sys.exit(1)
    
    def generate_chart(
        self,
        chart_type: str,
        chart_data: Dict,
        output_path: str,
        entry_id: str
    ) -> Optional[str]:
        """
        Generate a single chart

        Args:
            chart_type: Chart type (bar/scatter/pie)
            chart_data: Chart data
            output_path: Output path
            entry_id: Entry ID

        Returns:
            Returns image path on success, None on failure
        """
        config = PipelineConfig(
            chart_type=chart_type,
            global_figsize=self.figsize
        )
        
        try:
            if chart_type == "bar":
                draw__1_bar__func_1(
                    args=config,
                    bar_data=chart_data["bar_data"],
                    bar_labels=chart_data["bar_labels"],
                    bar_colors=chart_data["bar_colors"],
                    x_label=chart_data["x_label"],
                    y_label=chart_data["y_label"],
                    img_title=chart_data["img_title"],
                    label_angle=45,
                    horizontal=False,
                    show_text_label=True,
                    show_legend=True,
                    change_x_axis_pos=False,
                    change_y_axis_pos=False,
                    img_save_name=output_path
                )
            elif chart_type == "scatter":
                draw__3_scatter__func_1(
                    args=config,
                    scatter_x_data=chart_data["scatter_x_data"],
                    scatter_y_data=chart_data["scatter_y_data"],
                    scatter_labels=chart_data["scatter_labels"],
                    scatter_colors=chart_data["scatter_colors"],
                    scatter_sizes=chart_data["scatter_sizes"],
                    x_label=chart_data["x_label"],
                    y_label=chart_data["y_label"],
                    img_title=chart_data["img_title"],
                    show_legend=True,
                    img_save_name=output_path
                )
            elif chart_type == "pie":
                draw__8_pie__func_1(
                    args=config,
                    pie_data=chart_data["pie_data"],
                    pie_labels=chart_data["pie_labels"],
                    pie_colors=chart_data["pie_colors"],
                    img_title=chart_data["img_title"],
                    show_percentages=True,
                    show_legend=True,
                    img_save_name=output_path
                )
            else:
                self._log(f"Unsupported chart type: {chart_type}", "warning")
                return None
            
            # Close figure to release memory
            plt.close('all')
            
            self.stats['total_charts'] += 1
            self.stats['charts_by_type'][chart_type] = \
                self.stats['charts_by_type'].get(chart_type, 0) + 1
            
            return output_path
            
        except Exception as e:
            self._log(f"{chart_type} chart generation failed: {e}", "error")
            plt.close('all')
            return None
    
    def generate_qa(
        self,
        chart_type: str,
        chart_data: Dict,
        chart_id: str
    ) -> List[Dict]:
        """
        Generate QA data

        Args:
            chart_type: Chart type
            chart_data: Chart data
            chart_id: Chart ID

        Returns:
            QA data list
        """
        try:
            if chart_type == "bar":
                config = PipelineConfig(chart_type="bar")
                generator = BarChartGenerator(config, chart_id)
                qa_list = generator.chart_qa_generator(
                    chart_metadata=chart_data,
                    random_seed=self.random_seed,
                    num_questions=self.num_questions
                )
                
                # Update statistics
                self.stats['total_questions'] += len(qa_list)
                self.stats['questions_by_type'][chart_type] = \
                    self.stats['questions_by_type'].get(chart_type, 0) + len(qa_list)
                
                for qa in qa_list:
                    level = qa.get('curriculum_level', '1')
                    self.stats['questions_by_level'][level] = \
                        self.stats['questions_by_level'].get(level, 0) + 1
                
                return qa_list
            
            # TODO: Support QA generation for scatter and pie
            # elif chart_type == "scatter":
            #     ...
            # elif chart_type == "pie":
            #     ...
            else:
                self._log(f"{chart_type} type does not support QA generation yet", "warning")
                return []
                
        except Exception as e:
            self._log(f"{chart_type} QA generation failed: {e}", "error")
            return []
    
    def process_entry(self, entry: Dict, entry_idx: int) -> List[Dict]:
        """
        Process a single metadata entry

        Args:
            entry: Metadata entry
            entry_idx: Entry index

        Returns:
            List of generated samples
        """
        # Extract entry information
        generation_id = entry.get('generation_id', f'gen_{entry_idx}')
        category_id = entry.get('category_id', entry_idx)
        category_name = entry.get('category_name', 'Unknown')
        semantic_concept = entry.get('semantic_concept', '')
        chart_entries = entry.get('chart_entries', {})
        
        samples = []
        
        # Process each chart type
        for chart_type in self.chart_types:
            if chart_type not in chart_entries:
                self._log(f"Skip {chart_type}: not found in metadata", "warning")
                continue
            
            chart_data = chart_entries[chart_type]
            
            # Generate chart ID and path
            chart_id = f"{chart_type}__img_{entry_idx}__category{category_id}"
            img_relative_path = f"./data/imgs/{chart_type}/single/{chart_id}.png"
            img_absolute_path = os.path.join(
                self.output_dir, "imgs", chart_type, "single", f"{chart_id}.png"
            )
            
            # Generate chart
            self._log(f"Generating {chart_type} chart...", "info")
            chart_path = self.generate_chart(
                chart_type=chart_type,
                chart_data=chart_data,
                output_path=img_absolute_path,
                entry_id=generation_id
            )
            
            if chart_path is None:
                continue
            
            self._log(f"{chart_type} chart saved", "success")
            
            # Generate QA
            self._log(f"Generating {chart_type} QA...", "info")
            qa_list = self.generate_qa(
                chart_type=chart_type,
                chart_data=chart_data,
                chart_id=chart_id
            )
            
            if qa_list:
                self._log(f"{chart_type}: generated {len(qa_list)} questions", "success")
            
            # Create sample data (following main.py format)
            for qa in qa_list:
                sample_id = qa.get('qa_id', f"{chart_id}_qa")
                
                # Generate mask_path (following main.py format)
                mask_data = qa.get('mask', {})
                mask_path = {}
                mask_indices = {}
                
                for step_key, indices in mask_data.items():
                    mask_filename = f"{sample_id}__mask_{step_key}.png"
                    mask_path[step_key] = f"./data/imgs/{chart_type}/single/{mask_filename}"
                    mask_indices[step_key] = indices
                
                sample = {
                    "qa_id": sample_id,
                    "qa_type": qa.get('qa_type', 'unknown'),
                    "chart_type": chart_type,
                    "category": category_name,
                    "category_id": category_id,
                    "semantic_concept": semantic_concept,
                    "curriculum_level": qa.get('curriculum_level', '1'),
                    "constraint": qa.get('constraint', ''),
                    "eval_mode": "labeled",
                    "img_path": img_relative_path,
                    "mask_path": mask_path,
                    "mask_indices": mask_indices,
                    "question": qa.get('question', ''),
                    "reasoning": qa.get('reasoning', {}),
                    "answer": qa.get('answer', '')
                }
                
                samples.append(sample)
        
        return samples
    
    def run(self):
        """Run the complete Pipeline"""
        start_time = datetime.now()
        
        # Print configuration
        print(f"\n{'='*80}")
        print("Chart QA Pipeline - Start Generation")
        print(f"{'='*80}")
        print(f"Input file: {self.input_json}")
        print(f"Output directory: {self.output_dir}")
        print(f"Chart types: {', '.join(self.chart_types)}")
        print(f"Questions per chart: {self.num_questions}")
        print(f"Random seed: {self.random_seed}")
        print(f"Figure size: {self.figsize}")
        if self.limit:
            print(f"Processing limit: first {self.limit} entries")
        print(f"{'='*80}\n")
        
        # Load metadata
        metadata_list = self.load_metadata()
        
        all_samples = []
        
        # Process each entry
        for idx, entry in enumerate(metadata_list, 1):
            generation_id = entry.get('generation_id', f'gen_{idx}')
            category_name = entry.get('category_name', 'Unknown')
            
            print(f"\n[{idx}/{len(metadata_list)}] Processing: {generation_id}")
            print(f"  Category: {category_name}")
            
            try:
                samples = self.process_entry(entry, idx)
                all_samples.extend(samples)
                self.stats['processed_entries'] += 1
                
            except Exception as e:
                self.stats['failed_entries'] += 1
                print(f"  ✗ Processing failed: {e}")
        
        # Build final output (dictionary keyed by qa_id, consistent with main.py format)
        self.evaluation_data = {}
        for sample in all_samples:
            qa_id = sample.get('qa_id')
            if qa_id:
                self.evaluation_data[qa_id] = sample
        
        # Save evaluation data
        self._save_evaluation_data()
        
        # Print statistics
        self._print_statistics()
        
        # Calculate elapsed time
        elapsed = datetime.now() - start_time
        print(f"\n✓ Complete! Total time: {elapsed.total_seconds():.2f} seconds")
        print(f"{'='*80}\n")
    
    def _save_evaluation_data(self):
        """Save evaluation data to JSON file"""
        output_path = os.path.join(self.output_dir, "evaluation_data.json")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Evaluation data saved to: {output_path}")
            
        except Exception as e:
            print(f"\n✗ Failed to save file: {e}")
    
    def _print_statistics(self):
        """Print statistics"""
        print(f"\n{'='*80}")
        print("Generation Statistics")
        print(f"{'='*80}")
        print(f"Total entries: {self.stats['total_entries']}")
        print(f"Successfully processed: {self.stats['processed_entries']}")
        print(f"Failed: {self.stats['failed_entries']}")
        print(f"Total charts: {self.stats['total_charts']}")
        print(f"Total questions: {self.stats['total_questions']}")
        
        print(f"\nStatistics by chart type:")
        for chart_type in self.chart_types:
            charts = self.stats['charts_by_type'].get(chart_type, 0)
            questions = self.stats['questions_by_type'].get(chart_type, 0)
            print(f"  {chart_type}: {charts} charts, {questions} questions")
        
        print(f"\nStatistics by difficulty level:")
        level_names = {
            '1': 'Easy (Level 1)',
            '2': 'Medium (Level 2)',
            '3': 'Hard (Level 3)'
        }
        for level, count in self.stats['questions_by_level'].items():
            print(f"  {level_names.get(level, f'Level {level}')}: {count} questions")
        
        print(f"{'='*80}")


def main():
    """Main function - Command line interface"""
    parser = argparse.ArgumentParser(
        description="Chart QA Pipeline - Integrated chart and QA generation for VLM Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (process all entries, generate bar charts)
  python chart_qa_pipeline.py
  
  # Specify input and output
  python chart_qa_pipeline.py --input my_metadata.json --output-dir ./my_data
  
  # Generate multiple chart types
  python chart_qa_pipeline.py --chart-types bar scatter pie
  
  # Generate 10 questions per chart
  python chart_qa_pipeline.py --num-questions 10
  
  # Process only the first 5 entries (for testing)
  python chart_qa_pipeline.py --limit 5
  
  # Custom figure size
  python chart_qa_pipeline.py --figsize 12,8
  
  # Complete example
  python chart_qa_pipeline.py --input generated_metadata.json \\
                              --output-dir ./data \\
                              --chart-types bar \\
                              --num-questions 20 \\
                              --limit 10

Output structure:
  {output_dir}/
  ├── imgs/
  │   ├── bar/single/
  │   │   └── bar__img_1__category1.png
  │   ├── scatter/single/
  │   │   └── scatter__img_1__category1.png
  │   └── pie/single/
  │       └── pie__img_1__category1.png
  └── evaluation_data.json  (format consistent with main.py, dictionary keyed by qa_id)
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='generated_metadata.json',
        help='Input metadata JSON file path (default: generated_metadata.json)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./data',
        help='Output directory (default: ./data)'
    )
    
    parser.add_argument(
        '--chart-types',
        nargs='+',
        default=['bar'],
        choices=['bar', 'scatter', 'pie'],
        help='Chart types to generate (default: bar)'
    )
    
    parser.add_argument(
        '--num-questions',
        type=int,
        default=20,
        help='Number of questions to generate per chart (default: 20)'
    )
    
    parser.add_argument(
        '--random-seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit the number of entries to process (default: process all)'
    )
    
    parser.add_argument(
        '--figsize',
        type=str,
        default='10,6',
        help='Figure size, format: width,height (default: 10,6)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Quiet mode, do not display detailed information'
    )
    
    args = parser.parse_args()
    
    # Parse figure size
    try:
        figsize_parts = args.figsize.split(',')
        figsize = (float(figsize_parts[0]), float(figsize_parts[1]))
    except (ValueError, IndexError):
        print(f"✗ Error: Invalid figure size format '{args.figsize}', should be 'width,height'")
        sys.exit(1)
    
    # Create and run Pipeline
    pipeline = ChartQAPipeline(
        input_json=args.input,
        output_dir=args.output_dir,
        num_questions=args.num_questions,
        random_seed=args.random_seed,
        chart_types=args.chart_types,
        limit=args.limit,
        figsize=figsize,
        verbose=not args.quiet
    )
    
    pipeline.run()


if __name__ == "__main__":
    main()
