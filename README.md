# ChartAgentVAGEN

A comprehensive chart generation system for creating charts with question-answer pairs, supporting various chart types with operator-based composition and masking capabilities.

## Overview

ChartAgentVAGEN generates charts (currently bar charts) with associated QA data using a flexible operator composition system. It supports generating original charts, masked charts, and corresponding mask files for training and evaluation purposes.

## System Architecture

### Core Components

```
chartAgentVAGEN/
├── main.py                    # Main entry point for chart generation
├── requirements.txt           # Python dependencies
├── templates/                 # Base classes and abstractions
│   ├── operator.py           # Operator base classes (Operator, OperatorResult)
│   ├── parser.py             # Operation parsing and execution
│   ├── question_generator.py  # Question generation base classes
│   ├── chart_generator.py    # Chart generator base class
│   └── run_draw.py           # Drawing pipeline base class
├── chartGenerators/          # Chart type implementations
│   └── bar_chart/           # Bar chart implementation
│       ├── bar.py            # Main bar chart drawing and generation
│       ├── bar_operator.py  # Bar chart operators (sum, mean, filter, etc.)
│       ├── bar_parser.py     # Bar chart operation parser
│       ├── bar_question_generator.py  # Bar chart question generators
│       └── bar_chart_generator.py    # Bar chart QA data generator
├── metadata/                 # Chart metadata and data
│   └── metadata.py          # Predefined chart data across 30 categories
├── utils/                     # Utility functions
│   ├── logger.py            # Logging utilities
│   ├── json_util.py          # JSON file operations
│   └── masks/                # Mask generation utilities
└── data/                      # Generated output (ignored by git)
    ├── imgs/                 # Generated chart images
    └── *__meta_qa_data.json  # Generated QA data files
```

### System Flow

1. **Metadata Loading**: Loads chart data from `metadata/metadata.py` (30 categories)
2. **Chart Generation**: Creates charts with various configurations (orientation, labels, legends, etc.)
3. **Operator Composition**: Generates questions using compositional operators:
   - **Zero-step operators**: `sum`, `mean`, `median`, `count`, `max`, `min`, `read`
   - **One-step operators**: `threshold`, `kth`, `topk`, `all`
   - **Composition**: Sequential (`h(f)`), Parallel (`h(f1, f2)`), Nested (`h(f1(f2))`)
4. **Mask Generation**: Creates masked images and mask files for training
5. **QA Data Export**: Saves question-answer pairs with reasoning steps

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd chartAgentVAGEN
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

The `requirements.txt` includes:
- `numpy` - Numerical operations
- `matplotlib` - Chart plotting
- `pillow` - Image processing
- `opencv-python` - Computer vision operations
- `pandas` - Data manipulation
- `scikit-learn` - Machine learning utilities
- `scikit-image` - Image processing
- `scipy` - Scientific computing
- `statsmodels` - Statistical modeling
- `seaborn` - Statistical visualization

## Usage

### Running the Main Pipeline

The main entry point is `main.py`, which provides a command-line interface for chart generation.

#### Basic Usage

Run with default settings (all stages, all metadata):
```bash
python main.py
```

#### Command-Line Options

```bash
python main.py [OPTIONS]
```

**Options:**

- `--chart-type {bar}`: Type of chart to generate (default: `bar`)
- `--stages STAGES`: Stages to run (default: `0123` = all stages)
  - `0`: Generate masked chart images
  - `1`: Generate original chart images
  - `2/3`: Generate mask files
- `--data-path PATH`: Base path for saving generated data (default: `./data`)
- `--chart-mode MODE`: Chart generation mode (default: `single`)
- `--figsize WIDTH,HEIGHT`: Figure size (default: `10,6`)
- `--gray-mask COLOR`: Gray color code for masking (default: `#CCCCCC`)

#### Examples

**Run only original image generation:**
```bash
python main.py --stages 1
```

**Run original and masked images:**
```bash
python main.py --stages 0,1
```

**Custom data path:**
```bash
python main.py --data-path ./custom_data
```

**Run specific stages:**
```bash
python main.py --stages 0123  # All stages
python main.py --stages 1     # Only original images
python main.py --stages 0,1   # Original and masked images
```

**View help:**
```bash
python main.py --help
```

### Output Structure

Generated files are saved in the `data/` directory:

```
data/
├── imgs/
│   └── bar/
│       └── single/
│           ├── bar__img_1__category1__angle30__vertical__labeled__w_legend__xtop__yleft.png
│           ├── bar__img_1__category1__angle30__vertical__labeled__w_legend__xtop__yleft_qa1__mask_step_1__gray_mask.png
│           └── ...
└── bar__meta_qa_data.json
```

The JSON file contains QA data with:
- `qa_id`: Unique question ID
- `question`: Generated question
- `answer`: Answer to the question
- `reasoning`: Step-by-step reasoning
- `mask`: Mask indices for each step
- `img_path`: Path to original chart image
- `mask_path`: Paths to masked chart images

## Operator System

### Zero-Step Operators (h)
Operators that compute values from bar data:
- `sum`: Sum of values
- `mean`: Average of values
- `median`: Median value
- `count`: Count of bars
- `max`: Maximum value
- `min`: Minimum value
- `read`: Read values from bars
- `diff`: Difference between two values

### One-Step Operators (f)
Operators that filter/select bars:
- `threshold`: Filter bars above/below threshold
- `kth`: Get k-th highest/lowest bar
- `topk`: Get top/bottom k bars
- `all`: Select all bars

### Composition Examples

**Sequential**: `sum(threshold(...))` - Sum of filtered values
```python
# What is sum of values of categories above 20?
```

**Parallel**: `diff(max(...), min(...))` - Difference between max and min
```python
# What is difference in values of largest values and smallest values?
```

**Nested**: `mean(topk(threshold(...)))` - Mean of top k filtered bars
```python
# What is mean values of top 3 categories of categories above 15?
```

## Project Structure Details

### Templates (`templates/`)
Base classes defining the framework:
- **Operator**: Abstract base for all operators with composition support
- **Parser**: Parses operation settings and executes operations
- **QuestionGenerator**: Generates natural language questions
- **ChartGenerator**: Generates QA data for charts

### Chart Generators (`chartGenerators/`)
Concrete implementations for each chart type:
- **bar_chart/**: Complete bar chart implementation with operators, parsers, and generators

### Metadata (`metadata/`)
- Contains predefined chart data organized by 30 categories (Media & Entertainment, Geography, Education, etc.)
- Each category has multiple chart entries with bar data, labels, colors, and descriptions

### Utils (`utils/`)
- **logger.py**: Logging system
- **json_util.py**: JSON file operations
- **masks/**: Mask generation for training data

## Development

### Adding New Chart Types

1. Create a new directory in `chartGenerators/` (e.g., `pie_chart/`)
2. Implement:
   - Operators (`pie_operator.py`)
   - Parser (`pie_parser.py`)
   - Question Generator (`pie_question_generator.py`)
   - Chart Generator (`pie_chart_generator.py`)
   - Main drawing class (`pie.py`)
3. Update `main.py` to support the new chart type

### Extending Operators

Operators are defined in `chartGenerators/{chart_type}/{chart_type}_operator.py`. They inherit from:
- `ZeroStepOperator` for value-computing operators
- `OneStepOperator` for filtering operators

## License

See `LICENSE` file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Notes

- Generated data is saved to `data/` directory (ignored by git)
- The system supports curriculum levels (1: simple, 2: moderate, 3: complex)
- Questions are generated with reasoning steps for interpretability
- Mask generation supports multi-step reasoning with individual masks per step

