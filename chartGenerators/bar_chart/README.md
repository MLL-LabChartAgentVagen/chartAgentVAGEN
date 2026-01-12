# Bar Chart Generator with QA Data

This module generates bar charts with question-answer (QA) pairs for visual question answering tasks. It creates original bar charts and corresponding bounding box annotations that highlight relevant chart elements for each question.

## Overview

The `main.py` file provides a complete pipeline for:
- Generating bar charts with customizable configurations (axis placement, labels, orientation, etc.)
- Creating QA pairs with questions about the chart data
- Generating bounding box annotations that highlight relevant bars for each question
- Managing metadata and output organization

## Features

- **Single Configuration per Chart**: Each chart entry generates only one randomly selected configuration (instead of all combinations), making the generation process more efficient
- **Configurable Generation**: Control the number of charts, questions per chart, output paths, and random seed
- **Custom Metadata Support**: Use default metadata or provide custom JSON metadata files
- **Bounding Box Highlighting**: Generates images with bounding boxes around relevant chart elements instead of masking
- **Reproducible**: Deterministic random selection ensures the same seed produces identical results
- **Automatic Directory Creation**: Automatically creates output directories if they don't exist

## Dependencies

```python
- numpy
- pandas
- matplotlib
- seaborn
- json
- random (standard library)
- pathlib (standard library)
```

## Installation

Ensure you're in the project root directory and all dependencies are installed in your Python environment.

## Usage

### Basic Usage

Run with default settings (processes all charts, 20 questions per chart):

```bash
python chartGenerators/bar_chart/main.py
```

### Command-Line Arguments

#### Chart Generation Options

- `--num-charts NUM_CHARTS`: Number of charts to randomly generate. If not specified, processes all charts from metadata.
- `--num-questions NUM_QUESTIONS`: Number of questions to generate per chart (default: 20)
- `--random-seed RANDOM_SEED`: Random seed for reproducibility (default: 42)

#### File Paths

- `--data-path DATA_PATH`: Base path for saving generated data (default: `./data`)
- `--metadata-path METADATA_PATH`: Path to custom metadata JSON file. If not specified, uses default `METADATA_BAR`.

#### Chart Configuration

- `--chart-mode CHART_MODE`: Mode of chart generation (default: `single`)
- `--stages STAGES`: Stages to run: `'0'`=bbox images, `'1'`=original images. Can be `'0'`, `'1'`, or `'01'` (default: `01`)
- `--figsize FIGSIZE`: Figure size as `'width,height'` (default: `10,6`)
- `--gray-mask GRAY_MASK`: Gray color code for masking (default: `#CCCCCC`)
- `--bbox-color BBOX_COLOR`: Color for bounding boxes (default: `#FF0000` = red)

### Examples

#### Generate 5 random charts with 10 questions each

```bash
python chartGenerators/bar_chart/main.py --num-charts 5 --num-questions 10
```

#### Use custom metadata and output path

```bash
python chartGenerators/bar_chart/main.py \
    --metadata-path ./custom_metadata.json \
    --data-path ./custom_output
```

#### Generate 10 charts with 15 questions, custom seed

```bash
python chartGenerators/bar_chart/main.py \
    --num-charts 10 \
    --num-questions 15 \
    --random-seed 123
```

#### Only generate original images (no bbox images)

```bash
python chartGenerators/bar_chart/main.py --stages 1
```

#### Full example with all options

```bash
python chartGenerators/bar_chart/main.py \
    --num-charts 5 \
    --num-questions 12 \
    --data-path ./my_output \
    --metadata-path ./my_metadata.json \
    --random-seed 42 \
    --bbox-color "#FF0000" \
    --stages 01 \
    --figsize 12,8
```

#### Show help

```bash
python chartGenerators/bar_chart/main.py --help
```

## How It Works

### Workflow

1. **Initialization**: 
   - Loads metadata (default or custom)
   - Creates output directories if needed
   - Initializes chart drawing functions

2. **Chart Selection**:
   - If `--num-charts` is specified, randomly selects that many chart entries
   - Otherwise, processes all charts from metadata

3. **Configuration Selection**:
   - For each chart entry, randomly selects ONE configuration from:
     - Chart direction: `vertical` or `horizontal`
     - Label display: `labeled`
     - X-axis position: `xtop` or `xbottom`
     - Y-axis position: `yleft` or `yright`
     - Legend: `w_legend`
     - Label angle: `30`, `45`, `60`, or `90` degrees
   - Uses deterministic randomness based on `random_seed + chart_idx` for reproducibility

4. **Chart Generation**:
   - Generates original chart image (if stage `1` is enabled)
   - Creates unique chart ID based on configuration

5. **QA Generation**:
   - Generates specified number of questions per chart
   - Each question includes reasoning steps and answer
   - Identifies relevant bars for each question

6. **Bounding Box Generation**:
   - For each QA pair, generates bounding box images (if stage `0` is enabled)
   - Highlights relevant bars with colored bounding boxes
   - Saves bbox images for each reasoning step

7. **Data Saving**:
   - Saves all QA data to JSON file
   - Updates progress after each chart

### Output Structure

```
{data_path}/
├── {chart_type}__meta_qa_data.json          # QA data for all charts
└── imgs/
    └── {chart_type}/
        └── {chart_mode}/
            ├── {chart_id}.png                # Original chart
            ├── {qa_id}__bbox_step_1__bbox.png
            ├── {qa_id}__bbox_step_2__bbox.png
            └── {qa_id}__bbox_answer__bbox.png
```

### QA Data Structure

Each QA entry in the JSON file contains:

```json
{
  "qa_id": "unique_identifier",
  "qa_type": "question_type",
  "chart_type": "single",
  "category": "category_id",
  "curriculum_level": "level",
  "constraint": "constraint_info",
  "eval_mode": "labeled",
  "img_path": "path/to/original/chart.png",
  "bbox_path": {
    "step_1": "path/to/bbox_step_1.png",
    "step_2": "path/to/bbox_step_2.png",
    "answer": "path/to/bbox_answer.png"
  },
  "bbox_indices": {
    "step_1": [0, 2],
    "step_2": [1, 3],
    "answer": [0, 1, 2, 3]
  },
  "question": "What is the question?",
  "reasoning": "Step-by-step reasoning",
  "answer": "Final answer"
}
```

## Key Functions and Classes

### Main Functions

- `draw__1_bar__func_1()`: Draws a standard bar chart
- `draw__1_bar__func_1__bbox()`: Draws a bar chart with bounding boxes around specified bars
- `load_metadata()`: Loads metadata from file or returns default
- `collect_all_chart_entries()`: Collects all chart entries from metadata

### Main Class

#### `BarChartRunDraw`

Main class that orchestrates the chart and QA generation process.

**Key Methods:**
- `__init__(args)`: Initializes the generator with configuration
- `run_draw_single_figure()`: Main method that runs the generation pipeline
- `_init_plot_functions()`: Initializes chart drawing functions
- `_plot_bbox_chart()`: Generates bounding box images
- `_save_chart_qa_data_to_json()`: Saves QA data to JSON file

## Configuration Details

### Chart Configurations

Each chart gets one randomly selected configuration from:

- **Direction**: `vertical` (bars go up) or `horizontal` (bars go left/right)
- **Label Angle**: `30`, `45`, `60`, or `90` degrees (for x-axis labels)
- **Text Labels**: Currently always `labeled` (shows values on bars)
- **Legend**: Currently always `w_legend` (shows legend)
- **X-axis Position**: `xtop` (top) or `xbottom` (bottom)
- **Y-axis Position**: `yleft` (left) or `yright` (right)

### Random Selection

The random selection is deterministic and reproducible:
- Uses `random.Random(seed + chart_idx)` for each chart
- Same seed + same chart index = same configuration
- Ensures reproducibility across runs

## Error Handling

- **Missing Directories**: Automatically creates output directories if they don't exist
- **Missing Metadata File**: Provides clear error message if custom metadata file is not found
- **Invalid Arguments**: Validates command-line arguments and provides helpful error messages

## Notes

- The code generates **one configuration per chart entry** (not all combinations)
- Bounding boxes are used instead of masks to highlight relevant information
- All random selections are deterministic based on the random seed
- The same chart entry with the same seed will always get the same configuration

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **File Not Found**: Check that metadata file paths are correct (relative or absolute)
3. **Permission Errors**: Ensure write permissions for output directories
4. **Memory Issues**: If generating many charts, consider using `--num-charts` to limit the number

## See Also

- `bar_chart_generator.py`: Handles QA generation logic
- `bar_operator.py`: Defines operators for chart data manipulation
- `bar_question_generator.py`: Generates natural language questions
- `bar_parser.py`: Parses operation settings into executable operators

