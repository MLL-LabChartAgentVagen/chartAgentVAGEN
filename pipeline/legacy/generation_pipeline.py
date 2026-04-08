"""
ChartAgentVAGEN - Gemini-Driven Synthetic Data Construction Pipeline
=====================================================================

A modular, multi-node pipeline for generating high-quality training samples
with RL-Ready outputs (Chain-of-Thought traces + Hard Negatives).

Architecture: LangGraph-style sequential workflow
LLM Backend: Google Gemini (gemini-1.5-pro / gemini-2.0-flash)

Pipeline Nodes:
- Node A: Topic Generation
- Node B: Data Fabrication
- Node C: Schema Mapping + Caption Generation (combined)

Author: ChartAgentVAGEN Team
Version: 1.0.1
"""

import json
import random
import hashlib
import logging
import io
from typing import TypedDict, Literal, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import pandas as pd
import numpy as np

from schemas.master_table import MasterTable
from adapters.basic_operators import (
    Filter, Project, GroupBy, Aggregate, Sort, Limit, Chain
)

logger = logging.getLogger(__name__)

# =============================================================================
# SECTION 1: CORE SCHEMA DEFINITIONS (The "Knowledge Base")
# =============================================================================

META_CATEGORIES = [
    "1 - Media & Entertainment",
    "2 - Geography & Demography",
    "3 - Education & Academia",
    "4 - Business & Industry",
    "5 - Major & Course",
    "6 - Animal & Zoology",
    "7 - Plant & Botany",
    "8 - Biology & Chemistry",
    "9 - Food & Nutrition",
    "10 - Space & Astronomy",
    "11 - Sale & Merchandise",
    "12 - Market & Economy",
    "13 - Sports & Athletics",
    "14 - Computing & Technology",
    "15 - Health & Medicine",
    "16 - Energy & Environment",
    "17 - Travel & Expedition",
    "18 - Arts & Culture",
    "19 - Communication & Collaboration",
    "20 - Language & Linguistics",
    "21 - History & Archaeology",
    "22 - Weather & Climate",
    "23 - Transportation & Infrastructure",
    "24 - Psychology & Personality",
    "25 - Materials & Engineering",
    "26 - Philanthropy & Charity",
    "27 - Fashion & Apparel",
    "28 - Parenting & Child Development",
    "29 - Architecture & Urban Planning",
    "30 - Gaming & Recreation",
]

class ChartType(Enum):
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    LINE = "line"
    HEATMAP = "heatmap"


# Schema definitions for each chart type
CHART_SCHEMAS = {
    ChartType.BAR: {
        "required_keys": ["bar_data", "bar_labels", "bar_colors", "x_label", "y_label", "img_title"],
        "data_constraints": {
            "bar_data": "list[float] - Numeric values, typically 5-15 items",
            "bar_labels": "list[str] - Category labels, same length as bar_data",
            "bar_colors": "list[str] - Hex color codes (#RRGGBB), same length as bar_data",
            "x_label": "str - X-axis label describing the categories",
            "y_label": "str - Y-axis label with units in parentheses",
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.SCATTER: {
        "required_keys": ["scatter_x_data", "scatter_y_data", "scatter_labels", "scatter_colors", 
                         "scatter_sizes", "x_label", "y_label", "img_title"],
        "data_constraints": {
            "scatter_x_data": "list[float] - X-coordinates",
            "scatter_y_data": "list[float] - Y-coordinates",
            "scatter_labels": "list[str] - Point labels",
            "scatter_colors": "list[str] - Hex color codes",
            "scatter_sizes": "list[float] - Point sizes (typically value * scaling_factor)",
            "x_label": "str - X-axis label with units",
            "y_label": "str - Y-axis label with units",
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.PIE: {
        "required_keys": ["pie_data", "pie_labels", "pie_colors", "pie_data_category", 
                         "pie_label_category", "img_title"],
        "data_constraints": {
            "pie_data": "list[float] - Numeric values (will be converted to percentages)",
            "pie_labels": "list[str] - Slice labels",
            "pie_colors": "list[str] - Hex color codes",
            "pie_data_category": 'dict with keys "singular" and "plural" describing what data represents',
            "pie_label_category": 'dict with keys "singular" and "plural" describing the label entities',
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.HISTOGRAM: {
        "required_keys": ["histogram_data", "bin_edges", "x_label", "y_label", "img_title",
                         "chart_color", "tick_step"],
        "data_constraints": {
            "histogram_data": "list[float] - Raw data points to be binned",
            "bin_edges": "list[float] - Explicit bin boundary values",
            "x_label": "str - X-axis label describing the measured variable",
            "y_label": "str - Y-axis label (typically 'Frequency' or 'Count')",
            "img_title": "str - Descriptive chart title",
            "chart_color": "str - Single hex color code for all bars (#RRGGBB)",
            "tick_step": "int - Show a tick label every N bins"
        }
    },
    ChartType.LINE: {
        "required_keys": ["line_data", "line_labels", "line_category", "line_colors",
                         "x_labels", "x_label", "y_label", "img_title"],
        "data_constraints": {
            "line_data": "list[list[float]] - 2-D array, one sub-list per series",
            "line_labels": "list[str] - Series names, same length as line_data",
            "line_category": 'dict with keys "singular" and "plural" describing the entity type',
            "line_colors": "list[str] - Hex color codes, same length as line_data",
            "x_labels": "list - X-axis tick values (e.g. years), same length as each series",
            "x_label": "str - X-axis title",
            "y_label": "str - Y-axis title with units",
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.HEATMAP: {
        "required_keys": ["heatmap_data", "heatmap_category", "x_labels", "y_labels",
                         "x_label", "y_label", "img_title"],
        "data_constraints": {
            "heatmap_data": "list[list[float]] - 2-D matrix (rows × cols)",
            "heatmap_category": 'dict with keys "singular" and "plural" describing the cell values',
            "x_labels": "list[str] - Column header labels",
            "y_labels": "list[str] - Row header labels",
            "x_label": "str - X-axis title",
            "y_label": "str - Y-axis title",
            "img_title": "str - Descriptive chart title"
        }
    }
}


# =============================================================================
# SECTION 2: STATE DEFINITIONS FOR LANGGRAPH
# =============================================================================

@dataclass
class MasterDataRecord:
    """Raw data output from Node B (Data Fabricator)"""
    entities: list[str]           # Entity names (e.g., ["Netflix", "Disney+", ...])
    primary_values: list[float]   # Main metric values
    secondary_values: list[float] # Secondary metric (for scatter plots)
    tertiary_values: list[float]  # Tertiary metric (for scatter sizes)
    unit_primary: str             # Unit for primary values
    unit_secondary: str           # Unit for secondary values
    entity_type_singular: str     # e.g., "streaming service"
    entity_type_plural: str       # e.g., "streaming services"
    metric_name_primary: str      # e.g., "Monthly Subscribers"
    metric_name_secondary: str    # e.g., "Annual Revenue"
    statistical_properties: dict  # Trends, outliers, clusters info


class PipelineState(TypedDict):
    """Complete state object passed through the LangGraph pipeline"""
    # Node A outputs
    category_id: int
    category_name: str
    semantic_concept: str
    topic_description: str
    
    # Node B outputs
    master_data: Any  # MasterTable (new) or dict (legacy)
    
    # Node C outputs
    chart_entries: dict[str, dict]  # {chart_type: metadata_dict}
    
    # Node D outputs
    captions: dict[str, dict]  # {chart_type: {ground_truth_caption}}
    
    # Metadata
    generation_id: str
    timestamp: str
    

# =============================================================================
# SECTION 3: LLM SYSTEM PROMPTS
# =============================================================================

PROMPT_NODE_A_TOPIC_AGENT = """You are a Topic Generation Agent for a chart data synthesis pipeline.

## Your Role
Generate diverse, realistic topics for data visualization WITHIN the assigned category.

## CRITICAL: Autonomous Diversity Strategy

To avoid model collapse and ensure maximum diversity, YOU MUST autonomously vary these dimensions:

1. **Scale Dimension**: 
   - Micro: Individual items, specific products, single entities
   - Meso: Cities, companies, categories
   - Macro: Countries, industries, global comparisons
   - Meta: Cross-domain, abstract metrics

2. **Temporal Dimension**:
   - Historical: Pre-2010, decade-specific analysis
   - Current: 2020-2025, recent trends
   - Projected: Future predictions, forecasts
   - Timeless: Universal patterns, non-temporal data

3. **Geographic Scope**:
   - Local: City-level, regional
   - National: Country-specific
   - International: Cross-country comparisons
   - Global: Worldwide aggregates

4. **Specificity Level**:
   - Mainstream: Well-known entities, popular topics
   - Specialized: Industry-specific, technical domains
   - Niche: Obscure but valid topics, emerging areas
   - Cross-disciplinary: Unexpected combinations

5. **Metric Types**:
   - Counts: Absolute numbers, quantities
   - Rates: Percentages, ratios, per-capita
   - Monetary: Revenue, costs, valuations
   - Physical: Weights, distances, volumes
   - Temporal: Durations, frequencies

**For EACH generation**: Consciously select a DIFFERENT combination of these dimensions to create unique topics within the assigned category.

**Example Variations Within "Media & Entertainment"**:
- Micro + Current + Niche: "Average watch time of vertical short-form videos by creator tier (2024)"
- Macro + Historical + Mainstream: "Global box office revenue by film genre (2010-2020)"
- Meso + Projected + Specialized: "Podcast advertising revenue projections by category (2025-2027)"

## Assigned Category (User-Specified)
**{category_name}** (ID: {category_id})

You MUST generate a topic that belongs to this category.

## Output Format
Return a JSON object with these exact keys:
{{
    "semantic_concept": "<specific topic, 3-8 words>",
    "topic_description": "<one sentence explaining what data would be visualized>",
    "suggested_entities": ["<entity1>", "<entity2>", ...],  // 8-12 entities
    "suggested_metrics": ["<metric1>", "<metric2>", "<metric3>"],  // 2-3 quantifiable metrics
    "domain_context": "<brief domain background for realistic data generation>"
}}

## Diversity Requirements (Critical: Avoid Repetitive Topics)
- Vary between micro (individual items) and macro (countries, industries) scales
- Include both well-known and obscure topics within this category
- Balance between contemporary (2020s) and timeless topics
- Consider international perspectives, not just US-centric
- Generate UNIQUE topics - avoid repeating similar concepts

## Examples of Good Semantic Concepts for Different Categories

### Media & Entertainment
- "Streaming platform subscriber growth 2020-2024"
- "Box office revenue by film genre in Asia"
- "Podcast listening hours by age demographic"

### Geography & Demography  
- "Urban population density in European capitals"
- "Migration patterns of coastal cities"
- "Median household income by region"

### Business & Industry
- "Market capitalization of semiconductor companies"
- "Supply chain disruptions by industry sector"
- "Corporate carbon emissions by Fortune 500 companies"

### Health & Medicine
- "Hospital bed capacity by metropolitan area"
- "Vaccination rates across different age groups"
- "Mental health service availability by country"

### Education & Academia
- "University research funding by discipline"
- "Student-teacher ratios in international schools"
- "Graduate employment rates by major"

### Technology & Computing
- "Cloud service market share by provider"
- "Programming language popularity trends"
- "Semiconductor chip production capacity"

## Anti-patterns to Avoid
- Generic concepts: "Sales data", "Population statistics"
- Overly broad: "Technology trends", "Economic indicators"
- Fictional: Made-up companies, imaginary species
- Repetitive: Topics too similar to recently generated ones
"""

PROMPT_NODE_B_DATA_FABRICATOR = """You are a Statistical Data Fabrication Agent specializing in generating realistic synthetic datasets for Data Analysis.

## Your Role
Generate a **Master Data Table** in CSV format that represents a rich, multi-dimensional dataset suitable for various chart types (Bar, Line, Scatter, Pie).

## CRITICAL: Star Schema & Data Diversity
Your output MUST be a structured table with the following column categories:

### 1. Temporal Backbone (REQUIRED: 1+ Date/Time column)
- Include a date-related column (e.g., Date, Year, Month, Quarter, Period)
- Format: YYYY-MM-DD, YYYY, Q1-2024, Jan-2024, etc.

### 2. Dimensional Diversity (REQUIRED: 2+ Categorical columns)
- Include at least 2 categorical/entity columns
- Examples: Region, Category, Product, Company, Country, Segment
- These become the natural grouping dimensions for charts

### 3. Metric Correlation (REQUIRED: 2+ Numeric columns)
- Include at least 2 numeric measurement columns
- Primary metric: the main value being measured
- Secondary metric: a correlated or contrasting measurement
- Optional: Additional metrics for scatter sizes, etc.

## Statistical Pattern Injection (VARY EACH TIME)
For EACH generation, consciously choose ONE pattern from each:

### Distribution Type:
- **Normal**: Values cluster around mean +/- 1 SD
- **Power Law**: Few dominant values, many small (80-20 rule)
- **Bimodal**: Two distinct clusters
- **Exponential Decay**: Sharp ranked decline

### Correlation Pattern (between numeric columns):
- **Strong Positive** (r=0.7-0.9): Both increase together
- **Moderate** (r=0.4-0.6): Visible but noisy
- **Weak/None** (r=-0.2-0.2): No clear pattern
- **Negative** (r=-0.5 to -0.8): Inverse relationship

### Outlier Strategy:
- No outliers, single outlier (2-5x median), or multiple outliers

## Input Context
Category: {category_name}
Semantic Concept: {semantic_concept}
Topic Description: {topic_description}
Suggested Entities: {suggested_entities}
Suggested Metrics: {suggested_metrics}
Domain Context: {domain_context}

## Output Format: Pure CSV
- Return **ONLY** the raw CSV content.
- No markdown formatting, no code blocks, no intro/outro text.
- Header row is required.
- Use standard comma separation.
- 15-25 rows of data (not counting header).
- Values must be realistic for the domain.

## Example Output Structure (DO NOT copy this data, generate fresh):
Date,Region,Product,Revenue,Units_Sold,Customer_Satisfaction
2024-01,North,Widget_A,45200,1200,4.2
2024-01,South,Widget_B,38100,980,3.8

## Quality Checklist
- Has at least 1 temporal column
- Has at least 2 categorical columns
- Has at least 2 numeric columns
- Values are within realistic domain ranges
- Entity names are real and recognizable
- Output is PURE CSV only - no markdown, no JSON, no explanation
"""




PROMPT_NODE_C_SCHEMA_MAPPER = """You are a Schema Mapping Agent that transforms raw data into strict chart metadata formats.

## Your Role
Take Master Data and produce valid metadata dictionaries for BAR, SCATTER, PIE, HISTOGRAM, LINE, and HEATMAP chart types.

## Input Master Data
{master_data_json}

## CRITICAL: Exact Schema Specifications

### BAR Chart Schema
```json
{{
    "bar_data": [<float>, ...],           // Primary values, 8-12 items
    "bar_labels": ["<str>", ...],         // Entity names, same length
    "bar_colors": ["#RRGGBB", ...],       // Hex colors, same length, visually distinct
    "x_label": "<str>",                   // Describes the entities (e.g., "Streaming Services")
    "y_label": "<str>",                   // Metric + unit (e.g., "Subscribers (Millions)")
    "img_title": "<str>"                  // Descriptive title (e.g., "Top Streaming Platforms by Subscriber Count")
}}
```

### SCATTER Chart Schema
```json
{{
    "scatter_x_data": [<float>, ...],     // Secondary values as X coordinates
    "scatter_y_data": [<float>, ...],     // Primary values as Y coordinates
    "scatter_labels": ["<str>", ...],     // Entity names
    "scatter_colors": ["#RRGGBB", ...],   // Hex colors
    "scatter_sizes": [<float>, ...],      // Tertiary values * scaling_factor (aim for 50-500 range)
    "x_label": "<str>",                   // X-axis: secondary metric + unit
    "y_label": "<str>",                   // Y-axis: primary metric + unit  
    "img_title": "<str>"                  // Title showing relationship (e.g., "Revenue vs User Base")
}}
```

### PIE Chart Schema
```json
{{
    "pie_data": [<float>, ...],           // Primary values (will auto-convert to %)
    "pie_labels": ["<str>", ...],         // Entity names
    "pie_colors": ["#RRGGBB", ...],       // Hex colors
    "pie_data_category": {{
        "singular": "<what one slice represents>",
        "plural": "<what all slices represent>"
    }},
    "pie_label_category": {{
        "singular": "<entity type singular>",
        "plural": "<entity type plural>"
    }},
    "img_title": "<str>"                  // Title (e.g., "Market Share of Streaming Services")
}}
```

### HISTOGRAM Chart Schema
```json
{{
    "histogram_data": [<float>, ...],     // Raw data points to be binned (30-100+ values)
    "bin_edges": [<float>, ...],          // Explicit bin boundary values (N+1 edges for N bins)
    "x_label": "<str>",                   // X-axis: measured variable (e.g., "Response Time (ms)")
    "y_label": "<str>",                   // Y-axis: typically "Frequency" or "Count"
    "img_title": "<str>",                 // Descriptive title (e.g., "Distribution of Server Response Times")
    "chart_color": "#RRGGBB",             // Single hex color for all bars
    "tick_step": <int>                    // Show a tick label every N bins (e.g., 1, 2, 5)
}}
```

### LINE Chart Schema
```json
{{
    "line_data": [[<float>, ...], ...],   // 2-D array, one sub-list per series
    "line_labels": ["<str>", ...],        // Series names, same length as line_data
    "line_category": {{
        "singular": "<entity type singular>",
        "plural": "<entity type plural>"
    }},
    "line_colors": ["#RRGGBB", ...],      // Hex colors, same length as line_data
    "x_labels": [<value>, ...],           // X-axis tick values (e.g., years), same length as each series
    "x_label": "<str>",                   // X-axis title (e.g., "Year")
    "y_label": "<str>",                   // Y-axis title with units (e.g., "Revenue ($ Billion)")
    "img_title": "<str>"                  // Descriptive title (e.g., "Revenue Trends by Company (2018-2024)")
}}
```

### HEATMAP Chart Schema
```json
{{
    "heatmap_data": [[<float>, ...], ...], // 2-D matrix (rows × cols)
    "heatmap_category": {{
        "singular": "<what one cell value represents>",
        "plural": "<what all cell values represent>"
    }},
    "x_labels": ["<str>", ...],           // Column header labels
    "y_labels": ["<str>", ...],           // Row header labels
    "x_label": "<str>",                   // X-axis title
    "y_label": "<str>",                   // Y-axis title
    "img_title": "<str>"                  // Descriptive title (e.g., "Correlation of Skills Across Roles")
}}
```

## Color Palette Guidelines

**IMPORTANT**: Use visually distinct colors that vary across generations.

### Color Selection Strategy (vary each time):

1. **Vibrant Palette** (high saturation):
   - ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D"]

2. **Professional Palette** (muted, business):
   - ["#2E4057", "#048A81", "#54C6EB", "#F18F01", "#C73E1D", "#6A994E", "#BC4B51", "#5A189A"]

3. **Pastel Palette** (soft, light):
   - ["#B4E7CE", "#FFE5B4", "#FFC8DD", "#CAF0F8", "#E0BBE4", "#FFDAB9", "#C5E1A5", "#B39DDB"]

4. **Earth Tones** (natural, warm):
   - ["#8B4513", "#A0522D", "#CD853F", "#DEB887", "#F4A460", "#BC8F8F", "#DAA520", "#CD5C5C"]

5. **Neon/Bold** (high contrast):
   - ["#FF006E", "#FB5607", "#FFBE0B", "#8338EC", "#3A86FF", "#06FFA5", "#FF006A", "#7209B7"]

6. **Cool Tones** (blues and greens):
   - ["#03045E", "#0077B6", "#00B4D8", "#90E0EF", "#06D6A0", "#073B4C", "#118AB2", "#06FFA5"]

7. **Warm Tones** (reds and oranges):
   - ["#9B2226", "#AE2012", "#BB3E03", "#CA6702", "#EE9B00", "#E9D8A6", "#94D2BD", "#005F73"]

**Instructions**:
- For each generation, mentally rotate through palette styles (1→2→3→...→7→1)
- Due to temperature > 0.9, your selection will naturally vary
- Ensure adjacent colors have sufficient contrast (avoid similar hues next to each other)
- For branded entities (e.g., Netflix, Spotify), you may use their actual brand colors

## Scatter Size Calculation
scatter_sizes = [tertiary_value * scaling_factor for each entity]
Choose scaling_factor so sizes range roughly 50-500:
- If tertiary max < 10: scaling_factor ≈ 50-100
- If tertiary max 10-100: scaling_factor ≈ 10-50
- If tertiary max > 100: scaling_factor ≈ 1-10

## Output Format
Return a JSON object with six keys:
{{
    "bar": {{ <bar schema fields> }},
    "scatter": {{ <scatter schema fields> }},
    "pie": {{ <pie schema fields> }},
    "histogram": {{ <histogram schema fields> }},
    "line": {{ <line schema fields> }},
    "heatmap": {{ <heatmap schema fields> }}
}}

## Validation Checklist (MUST pass all)
✓ All arrays within each chart have identical length
✓ All color codes are valid 6-digit hex with # prefix
✓ pie_data_category, pie_label_category, line_category, and heatmap_category all have "singular" and "plural" keys
✓ histogram bin_edges has exactly one more element than the number of desired bins
✓ Each sub-list in line_data has the same length as x_labels
✓ heatmap_data has len(y_labels) rows and len(x_labels) columns
✓ Labels are human-readable (no underscores, proper capitalization)
✓ Titles are descriptive and grammatically correct
✓ Units are consistently formatted (e.g., always "$ Million" not "$M" or "Million $")
"""

PROMPT_NODE_D_RL_CAPTIONER = """You are an RL Caption Generation Agent that produces training data for chart understanding models.

## Your Role
Generate a ground truth caption for the chart - an accurate, comprehensive description.

## Input Chart Metadata
Chart Type: {chart_type}
Metadata: {chart_metadata_json}

## Output Specifications

## Caption Style Diversity

To prevent repetitive caption patterns, vary your writing style across generations:

### Structural Variations:
1. **Top-down**: Start with overview, then details
   - "This chart shows market share distribution. Netflix leads with 45%, followed by..."

2. **Bottom-up**: Start with specific data, then generalize
   - "Netflix holds 45% market share, significantly higher than Disney+ at 25%. Overall, the market shows..."

3. **Comparative**: Emphasize relationships between entities
   - "Netflix's 45% share is nearly double that of Disney+ (25%), while smaller players..."

4. **Analytical**: Focus on patterns and trends
   - "The distribution reveals a power-law pattern with one dominant player controlling nearly half..."

### Tone Variations:
- **Neutral/Academic**: Factual, precise language
- **Journalistic**: Engaging, story-like presentation
- **Technical**: Emphasize statistical properties and metrics

### Length Variations:
- **Concise**: 2 sentences, 40-60 words
- **Standard**: 3 sentences, 60-80 words  
- **Detailed**: 4 sentences, 80-100 words

**For each generation**: Naturally vary structure, tone, and length based on the data characteristics. Temperature > 1.0 will help produce diverse phrasings.

### Ground Truth Caption
A factual description covering:
- What the chart shows (topic, entities, metrics)
- Key insights (highest/lowest values, notable patterns)
- Quantitative details (specific numbers for top 2-3 items)
- Overall trend or distribution pattern

Length: 2-4 sentences, 50-100 words

## Output Format
Return a JSON object with only the ground truth caption:
{{
    "ground_truth_caption": "<accurate description>"
}}

## Quality Requirements
- Caption must be 100% accurate to the input data
- Include specific numerical values for top performers
- Describe the overall pattern or distribution
- Be concise but comprehensive
"""


# =============================================================================
# SECTION 4: NODE IMPLEMENTATIONS
# =============================================================================

class NodeA_TopicAgent:
    """
    Node A: Topic Concept Generation (User-Specified Category Version)
    
    Improvements over old implementation:
    - User MUST manually specify category_id and category_name
    - LLM no longer selects category, but generates diverse topics within specified category
    - Maintains diversity tracker to ensure topic variety in batch generation
    
    Responsibilities:
    - Generate semantic concept within user-specified category
    - Provide entity and metric suggestions
    - Provide domain context for Node B
    """
    
    def __init__(self, llm_client, diversity_tracker: Optional[dict] = None):
        self.llm = llm_client
        self.diversity_tracker = diversity_tracker or {
            "used_concepts": [],      # Previously used concepts
            "used_entities": []        # Previously used entity types
        }
    
    def get_system_prompt(self, category_id: int, category_name: str) -> str:
        """Generate system prompt for specified category"""
        return PROMPT_NODE_A_TOPIC_AGENT.format(
            category_id=category_id,
            category_name=category_name
        )
    
    def get_user_prompt(self, constraints: Optional[dict] = None) -> str:
        """Generate user prompt with constraints and diversity hints"""
        prompt = "Generate a new, unique topic for chart data synthesis within the assigned category."
        
        # Add constraints
        if constraints:
            if constraints.get("avoid_concepts"):
                recent_concepts = constraints["avoid_concepts"][-10:]  # Last 10
                if recent_concepts:
                    prompt += f"\n\n**AVOID these recently used concepts:**\n"
                    for concept in recent_concepts:
                        prompt += f"- {concept}\n"
            
            if constraints.get("theme_hint"):
                prompt += f"\n\n**Theme suggestion:** {constraints['theme_hint']}"
            
            if constraints.get("scale_preference"):
                prompt += f"\n\n**Scale preference:** {constraints['scale_preference']}"
        
        # Enhanced diversity hints with anti-repetition context
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-10:]
        if recent_concepts:
            prompt += f"\n\n**Context: Recently generated concepts (for awareness, not constraints):**"
            for i, concept in enumerate(recent_concepts[-5:], 1):
                prompt += f"\n  {i}. {concept}"
            
            prompt += "\n\n**Your task**: Generate a concept that explores a DIFFERENT aspect of the category."
            prompt += "\n- Use a different scale (micro/meso/macro) than recent examples"
            prompt += "\n- Choose a different time period or geographic focus"
            prompt += "\n- Select different metric types or entity categories"
            prompt += "\n\nDue to your stochastic sampling (temperature > 1.0), naturally vary the theme, scale, and specificity."
        
        return prompt
    
    def validate_output(self, response: dict, category_name: str) -> tuple[bool, list[str]]:
        """Validate Node A output"""
        errors = []
        
        # Check required fields
        required_fields = [
            "semantic_concept", "topic_description", 
            "suggested_entities", "suggested_metrics", "domain_context"
        ]
        
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")
        
        # Check data types
        if "suggested_entities" in response:
            if not isinstance(response["suggested_entities"], list):
                errors.append("suggested_entities must be a list")
            elif len(response["suggested_entities"]) < 8:
                errors.append(f"Need at least 8 entities, got {len(response['suggested_entities'])}")
        
        if "suggested_metrics" in response:
            if not isinstance(response["suggested_metrics"], list):
                errors.append("suggested_metrics must be a list")
            elif len(response["suggested_metrics"]) < 2:
                errors.append("Need at least 2 metrics")
        
        # Check for topic repetition
        semantic_concept = response.get("semantic_concept", "")
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-10:]
        
        for recent in recent_concepts:
            # Simple similarity check (can be improved with more sophisticated algorithms)
            if semantic_concept.lower() in recent.lower() or recent.lower() in semantic_concept.lower():
                errors.append(f"Concept too similar to recent: '{recent}'")
                break
        
        return len(errors) == 0, errors
    
    def __call__(
        self, 
        state: PipelineState, 
        category_id: int,
        category_name: str,
        constraints: Optional[dict] = None
    ) -> PipelineState:
        """
        Execute Node A and update state
        
        Args:
            state: Pipeline state object
            category_id: User-specified category ID (1-30)
            category_name: User-specified category name
            constraints: Optional constraints
                - avoid_concepts: list[str] - Concepts to avoid
                - theme_hint: str - Theme suggestion
                - scale_preference: str - Scale preference ("micro", "macro")
        
        Returns:
            Updated PipelineState
        """
        # Validate category
        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}. Must be between 1 and 30."
            )
        
        if category_name not in META_CATEGORIES:
            raise ValueError(
                f"Invalid category_name: {category_name}. "
                f"Must be one of the 30 predefined categories."
            )
        
        # Prepare constraints (including info from diversity tracker)
        full_constraints = constraints or {}
        if "avoid_concepts" not in full_constraints:
            full_constraints["avoid_concepts"] = self.diversity_tracker.get("used_concepts", [])
        
        # Call LLM to generate topic
        response = self.llm.generate_json(
            system=self.get_system_prompt(category_id, category_name),
            user=self.get_user_prompt(full_constraints),
            temperature=1.2  # High temperature for maximum topic diversity
        )
        
        # Validate output
        is_valid, errors = self.validate_output(response, category_name)
        if not is_valid:
            # Warning but don't interrupt (allow to continue)
            print(f"Warning: Node A validation issues: {errors}")
        
        # Update diversity tracker
        self.diversity_tracker["used_concepts"].append(
            response.get("semantic_concept", "")
        )
        self.diversity_tracker["used_entities"].extend(
            response.get("suggested_entities", [])[:3]  # Only track first 3
        )
        
        # Update state (user-provided category + LLM-generated topic)
        state["category_id"] = category_id
        state["category_name"] = category_name
        state["semantic_concept"] = response.get("semantic_concept", "")
        state["topic_description"] = response.get("topic_description", "")
        
        # Store additional info for Node B (underscore prefix indicates internal variable)
        state["_suggested_entities"] = response.get("suggested_entities", [])
        state["_suggested_metrics"] = response.get("suggested_metrics", [])
        state["_domain_context"] = response.get("domain_context", "")
        
        return state


class NodeB_DataFabricator:
    """
    Node B: Statistical Data Generation (Star Schema / CSV Mode)
    
    Responsibilities:
    - Generate a Master Data Table in CSV format (rows & columns)
    - Parse LLM CSV output into a pandas DataFrame
    - Wrap in MasterTable with Star Schema validation
    - Retry on malformed output (up to max_retries)
    """
    
    MAX_RETRIES = 2
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return PROMPT_NODE_B_DATA_FABRICATOR
    
    def _clean_csv_response(self, raw: str) -> str:
        """Strip markdown fences and surrounding whitespace from LLM CSV output."""
        cleaned = raw.strip()
        # Remove markdown code fences
        if cleaned.startswith("```csv"):
            cleaned = cleaned[6:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()
    
    def validate_master_table(self, mt: MasterTable) -> tuple[bool, list[str]]:
        """Validate the MasterTable meets Star Schema requirements."""
        errors = []
        df = mt.df
        
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        if len(df) < 5:
            errors.append(f"Too few rows: {len(df)}, expected 15-25")
        
        # Check for numeric columns (need 2+)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(num_cols) < 2:
            errors.append(f"Need 2+ numeric columns, found {len(num_cols)}")
        
        # Check for categorical columns (need 2+)
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        if len(cat_cols) < 2:
            errors.append(f"Need 2+ categorical columns, found {len(cat_cols)}")
        
        return len(errors) == 0, errors
    
    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Node B: generate CSV data, parse into MasterTable."""
        system_prompt = PROMPT_NODE_B_DATA_FABRICATOR.format(
            category_name=state.get("category_name", ""),
            semantic_concept=state.get("semantic_concept", ""),
            topic_description=state.get("topic_description", ""),
            suggested_entities=state.get("_suggested_entities", []),
            suggested_metrics=state.get("_suggested_metrics", []),
            domain_context=state.get("_domain_context", "")
        )
        
        last_error = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                # Request CSV text (not JSON)
                raw_response = self.llm.generate(
                    system=system_prompt,
                    user="Generate the master data table now as pure CSV.",
                    temperature=1.0,
                    response_format="text"
                )
                
                csv_content = self._clean_csv_response(raw_response)
                
                # Parse into MasterTable
                mt = MasterTable.from_csv(
                    csv_content,
                    metadata={
                        "category": state.get("category_name", ""),
                        "concept": state.get("semantic_concept", ""),
                        "title": state.get("topic_description", ""),
                    }
                )
                
                # Validate
                is_valid, errors = self.validate_master_table(mt)
                if not is_valid:
                    logger.warning(
                        f"Node B attempt {attempt+1}: validation warnings: {errors}"
                    )
                    # Warnings are non-fatal; continue if we have valid data
                
                state["master_data"] = mt
                return state
                
            except (ValueError, Exception) as e:
                last_error = e
                logger.warning(
                    f"Node B attempt {attempt+1}/{self.MAX_RETRIES+1} failed: {e}"
                )
                if attempt < self.MAX_RETRIES:
                    continue
        
        raise ValueError(
            f"Node B failed after {self.MAX_RETRIES+1} attempts. "
            f"Last error: {last_error}"
        )


class NodeC_SchemaMapper:
    """
    Node C: One-to-Many Schema Transformation + Caption Generation
    
    Supports two modes controlled by ``use_relational_adapter``:
    
    1. **Relational Adapter (default, use_relational_adapter=True)**:
       Receives a ``MasterTable`` from Node B and applies relational
       operator chains (GroupBy, Sort, Limit, Project) to derive chart-
       specific data.  No LLM call is needed for the schema mapping
       itself — only for caption generation.
    
    2. **Legacy / Direct (use_relational_adapter=False)**:
       Passes the master data dict to the LLM for schema mapping,
       matching the original pipeline behaviour.
    
    Responsibilities:
    - Ensure strict schema compliance
    - Generate appropriate color palettes
    - Generate ground truth captions for each chart type
    """
    
    # Default color palette for generation
    DEFAULT_COLORS = [
        "#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8",
        "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1",
        "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
    ]
    
    def __init__(self, llm_client, use_relational_adapter: bool = True):
        self.llm = llm_client
        self.use_relational_adapter = use_relational_adapter
    
    # ------------------------------------------------------------------
    # Legacy helpers (used when use_relational_adapter=False)
    # ------------------------------------------------------------------
    
    def get_system_prompt(self) -> str:
        return PROMPT_NODE_C_SCHEMA_MAPPER
    
    def get_user_prompt(self, state: PipelineState) -> str:
        md = state['master_data']
        if isinstance(md, dict):
            data_str = json.dumps(md, indent=2)
        else:
            data_str = md.to_csv()
        return f"Transform this Master Data into BAR, SCATTER, and PIE chart schemas:\n\n{data_str}"
    
    def transform_to_bar(self, master_data: dict) -> dict:
        """Direct transformation to BAR schema (legacy fallback)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        return {
            "bar_data": master_data["primary_values"],
            "bar_labels": master_data["entities"],
            "bar_colors": colors,
            "x_label": master_data["entity_type_plural"].title(),
            "y_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "img_title": f"{master_data['metric_name_primary']} by {master_data['entity_type_singular'].title()}"
        }
    
    def transform_to_scatter(self, master_data: dict) -> dict:
        """Direct transformation to SCATTER schema (legacy fallback)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        # Calculate appropriate size scaling
        tertiary = master_data["tertiary_values"]
        max_tertiary = max(tertiary) if tertiary else 1
        if max_tertiary < 10:
            scale = 60
        elif max_tertiary < 100:
            scale = 20
        else:
            scale = 5
        
        return {
            "scatter_x_data": master_data["secondary_values"],
            "scatter_y_data": master_data["primary_values"],
            "scatter_labels": master_data["entities"],
            "scatter_colors": colors,
            "scatter_sizes": [v * scale for v in tertiary],
            "x_label": f"{master_data['metric_name_secondary']} ({master_data['unit_secondary']})",
            "y_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "img_title": f"{master_data['metric_name_primary']} vs {master_data['metric_name_secondary']}"
        }
    
    def transform_to_pie(self, master_data: dict) -> dict:
        """Direct transformation to PIE schema (legacy fallback)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        return {
            "pie_data": master_data["primary_values"],
            "pie_labels": master_data["entities"],
            "pie_colors": colors,
            "pie_data_category": {
                "singular": master_data["entity_type_singular"],
                "plural": master_data["entity_type_plural"]
            },
            "pie_label_category": {
                "singular": master_data["entity_type_singular"],
                "plural": master_data["entity_type_plural"]
            },
            "img_title": f"Distribution of {master_data['metric_name_primary']} by {master_data['entity_type_singular'].title()}"
        }
    
    def transform_to_histogram(self, master_data: dict) -> dict:
        """Direct transformation to HISTOGRAM schema (legacy fallback)"""
        values = master_data["primary_values"]
        counts, edges = np.histogram(values, bins='auto')
        return {
            "histogram_data": values,
            "bin_edges": edges.tolist(),
            "x_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "y_label": "Frequency",
            "img_title": f"Distribution of {master_data['metric_name_primary']}",
            "chart_color": self.DEFAULT_COLORS[0],
            "tick_step": 2,
        }
    
    def transform_to_line(self, master_data: dict) -> dict:
        """Direct transformation to LINE schema (legacy fallback)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        # Wrap primary_values as a single series
        return {
            "line_data": [master_data["primary_values"]],
            "line_labels": [master_data["metric_name_primary"]],
            "line_category": {
                "singular": master_data["entity_type_singular"],
                "plural": master_data["entity_type_plural"]
            },
            "line_colors": [colors[0]],
            "x_labels": master_data["entities"],
            "x_label": master_data["entity_type_plural"].title(),
            "y_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "img_title": f"{master_data['metric_name_primary']} Trend"
        }
    
    def transform_to_heatmap(self, master_data: dict) -> dict:
        """Direct transformation to HEATMAP schema (legacy fallback)"""
        n = len(master_data["entities"])
        # Create a single-row matrix from primary values
        return {
            "heatmap_data": [master_data["primary_values"]],
            "heatmap_category": {
                "singular": master_data["metric_name_primary"],
                "plural": master_data["metric_name_primary"]
            },
            "x_labels": master_data["entities"],
            "y_labels": [master_data["metric_name_primary"]],
            "x_label": master_data["entity_type_plural"].title(),
            "y_label": "Metric",
            "img_title": f"{master_data['metric_name_primary']} by {master_data['entity_type_singular'].title()}"
        }
    
    # ------------------------------------------------------------------
    # Schema validators (shared by both modes)
    # ------------------------------------------------------------------
    
    def validate_bar_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate BAR chart schema"""
        errors = []
        required = ["bar_data", "bar_labels", "bar_colors", "x_label", "y_label", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["bar_data"])
        if len(data["bar_labels"]) != n:
            errors.append(f"bar_labels length mismatch")
        if len(data["bar_colors"]) != n:
            errors.append(f"bar_colors length mismatch")
        
        # Validate hex colors
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        for i, color in enumerate(data["bar_colors"]):
            if not hex_pattern.match(color):
                errors.append(f"Invalid hex color at index {i}: {color}")
        
        return len(errors) == 0, errors
    
    def validate_scatter_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate SCATTER chart schema"""
        errors = []
        required = ["scatter_x_data", "scatter_y_data", "scatter_labels", 
                    "scatter_colors", "scatter_sizes", "x_label", "y_label", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["scatter_x_data"])
        for key in ["scatter_y_data", "scatter_labels", "scatter_colors", "scatter_sizes"]:
            if len(data[key]) != n:
                errors.append(f"{key} length mismatch")
        
        return len(errors) == 0, errors
    
    def validate_pie_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate PIE chart schema"""
        errors = []
        required = ["pie_data", "pie_labels", "pie_colors", 
                    "pie_data_category", "pie_label_category", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["pie_data"])
        if len(data["pie_labels"]) != n:
            errors.append("pie_labels length mismatch")
        if len(data["pie_colors"]) != n:
            errors.append("pie_colors length mismatch")
        
        # Validate category dicts
        for cat_key in ["pie_data_category", "pie_label_category"]:
            cat = data[cat_key]
            if not isinstance(cat, dict):
                errors.append(f"{cat_key} must be a dict")
            elif "singular" not in cat or "plural" not in cat:
                errors.append(f"{cat_key} must have 'singular' and 'plural' keys")
        
        return len(errors) == 0, errors
    
    def validate_histogram_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate HISTOGRAM chart schema"""
        errors = []
        required = ["histogram_data", "bin_edges", "x_label", "y_label", "img_title",
                    "chart_color", "tick_step"]
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        if errors:
            return False, errors
        if not isinstance(data["histogram_data"], list):
            errors.append("histogram_data must be a list")
        if not isinstance(data["bin_edges"], list):
            errors.append("bin_edges must be a list")
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        if not hex_pattern.match(str(data.get("chart_color", ""))):
            errors.append(f"Invalid chart_color: {data.get('chart_color')}")
        return len(errors) == 0, errors
    
    def validate_line_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate LINE chart schema"""
        errors = []
        required = ["line_data", "line_labels", "line_category", "line_colors",
                    "x_labels", "x_label", "y_label", "img_title"]
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        if errors:
            return False, errors
        n_series = len(data["line_data"])
        if len(data["line_labels"]) != n_series:
            errors.append("line_labels length must match number of series in line_data")
        if len(data["line_colors"]) != n_series:
            errors.append("line_colors length must match number of series in line_data")
        if n_series > 0 and data["x_labels"]:
            expected_len = len(data["line_data"][0])
            for i, series in enumerate(data["line_data"]):
                if len(series) != expected_len:
                    errors.append(f"line_data[{i}] length mismatch (expected {expected_len})")
            if len(data["x_labels"]) != expected_len:
                errors.append("x_labels length must match series length")
        cat = data.get("line_category", {})
        if not isinstance(cat, dict) or "singular" not in cat or "plural" not in cat:
            errors.append("line_category must have 'singular' and 'plural' keys")
        return len(errors) == 0, errors
    
    def validate_heatmap_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate HEATMAP chart schema"""
        errors = []
        required = ["heatmap_data", "heatmap_category", "x_labels", "y_labels",
                    "x_label", "y_label", "img_title"]
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        if errors:
            return False, errors
        n_rows = len(data["heatmap_data"])
        if len(data["y_labels"]) != n_rows:
            errors.append(f"y_labels length ({len(data['y_labels'])}) must match heatmap rows ({n_rows})")
        if n_rows > 0:
            n_cols = len(data["heatmap_data"][0])
            for i, row in enumerate(data["heatmap_data"]):
                if len(row) != n_cols:
                    errors.append(f"heatmap_data[{i}] has {len(row)} cols, expected {n_cols}")
            if len(data["x_labels"]) != n_cols:
                errors.append(f"x_labels length ({len(data['x_labels'])}) must match heatmap cols ({n_cols})")
        cat = data.get("heatmap_category", {})
        if not isinstance(cat, dict) or "singular" not in cat or "plural" not in cat:
            errors.append("heatmap_category must have 'singular' and 'plural' keys")
        return len(errors) == 0, errors
    
    def validate_caption_output(self, data: dict) -> tuple[bool, list[str]]:
        """Validate caption output structure"""
        errors = []
        
        if "ground_truth_caption" not in data:
            errors.append("Missing ground_truth_caption")
        elif not isinstance(data["ground_truth_caption"], str):
            errors.append("ground_truth_caption must be a string")
        elif len(data["ground_truth_caption"].strip()) == 0:
            errors.append("ground_truth_caption cannot be empty")
        
        return len(errors) == 0, errors
    
    # ------------------------------------------------------------------
    # Relational Adapter helpers (NEW — default mode)
    # ------------------------------------------------------------------
    
    def _pick_columns(self, mt: MasterTable):
        """Heuristically pick categorical and numeric columns from the MasterTable."""
        df = mt.df
        cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Filter out date-like strings from categorical
        non_date_cats = [
            c for c in cat_cols
            if not any(kw in c.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter'))
        ]
        entity_col = non_date_cats[0] if non_date_cats else (cat_cols[0] if cat_cols else None)
        primary_metric = num_cols[0] if len(num_cols) >= 1 else None
        secondary_metric = num_cols[1] if len(num_cols) >= 2 else None
        tertiary_metric = num_cols[2] if len(num_cols) >= 3 else None
        
        return entity_col, primary_metric, secondary_metric, tertiary_metric
    
    def _adapter_bar(self, mt: MasterTable) -> dict:
        """Bar: GroupBy(entity) -> Sum(primary) -> Sort(desc) -> Limit(10)"""
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive bar chart: missing entity or primary metric column")
        
        chain = Chain([
            GroupBy(by=[entity_col], agg={primary_metric: 'sum'}),
            Sort(column=primary_metric, ascending=False),
            Limit(10),
        ])
        result_df = chain.apply(mt.df)
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        return {
            "bar_data": result_df[primary_metric].tolist(),
            "bar_labels": result_df[entity_col].astype(str).tolist(),
            "bar_colors": colors,
            "x_label": entity_col,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} by {entity_col}",
        }
    
    def _adapter_scatter(self, mt: MasterTable) -> dict:
        """Scatter: Project(primary, secondary) -> Output"""
        entity_col, primary_metric, secondary_metric, tertiary_metric = self._pick_columns(mt)
        if not primary_metric or not secondary_metric:
            raise ValueError("Cannot derive scatter chart: need 2+ numeric columns")
        
        cols_to_project = [c for c in [entity_col, primary_metric, secondary_metric, tertiary_metric] if c]
        chain = Chain([Project(cols_to_project)])
        result_df = chain.apply(mt.df).dropna(subset=[primary_metric, secondary_metric])
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        # Compute scatter sizes from tertiary if available
        if tertiary_metric and tertiary_metric in result_df.columns:
            tertiary_vals = result_df[tertiary_metric].tolist()
            max_t = max(tertiary_vals) if tertiary_vals else 1
            scale = 60 if max_t < 10 else (20 if max_t < 100 else 5)
            sizes = [v * scale for v in tertiary_vals]
        else:
            sizes = [50] * n
        
        return {
            "scatter_x_data": result_df[secondary_metric].tolist(),
            "scatter_y_data": result_df[primary_metric].tolist(),
            "scatter_labels": result_df[entity_col].astype(str).tolist() if entity_col else [str(i) for i in range(n)],
            "scatter_colors": colors,
            "scatter_sizes": sizes,
            "x_label": secondary_metric,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} vs {secondary_metric}",
        }
    
    def _adapter_pie(self, mt: MasterTable) -> dict:
        """Pie: GroupBy(entity) -> Sum(primary) -> Sort(desc) -> Limit(8)"""
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive pie chart: missing entity or primary metric column")
        
        chain = Chain([
            GroupBy(by=[entity_col], agg={primary_metric: 'sum'}),
            Sort(column=primary_metric, ascending=False),
            Limit(8),
        ])
        result_df = chain.apply(mt.df)
        n = len(result_df)
        colors = self.DEFAULT_COLORS[:n] if n <= len(self.DEFAULT_COLORS) else (self.DEFAULT_COLORS * ((n // len(self.DEFAULT_COLORS)) + 1))[:n]
        
        return {
            "pie_data": result_df[primary_metric].tolist(),
            "pie_labels": result_df[entity_col].astype(str).tolist(),
            "pie_colors": colors,
            "pie_data_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "pie_label_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "img_title": f"Distribution of {primary_metric} by {entity_col}",
        }
    
    def _adapter_histogram(self, mt: MasterTable) -> dict:
        """Histogram: Take primary numeric column and compute bin distribution."""
        _, primary_metric, _, _ = self._pick_columns(mt)
        if not primary_metric:
            raise ValueError("Cannot derive histogram: missing numeric column")
        
        values = mt.df[primary_metric].dropna().tolist()
        counts, edges = np.histogram(values, bins='auto')
        
        return {
            "histogram_data": values,
            "bin_edges": edges.tolist(),
            "x_label": primary_metric,
            "y_label": "Frequency",
            "img_title": f"Distribution of {primary_metric}",
            "chart_color": self.DEFAULT_COLORS[0],
            "tick_step": max(1, len(edges) // 6),
        }
    
    def _adapter_line(self, mt: MasterTable) -> dict:
        """Line: Pivot entity × temporal → multi-series time data."""
        df = mt.df
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive line chart: missing entity or metric column")
        
        # Identify a temporal column
        temporal_col = None
        for col in df.columns:
            if any(kw in col.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter')):
                temporal_col = col
                break
        
        if temporal_col:
            # Pivot: each entity becomes a series, temporal becomes x-axis
            pivot = df.pivot_table(
                index=temporal_col, columns=entity_col,
                values=primary_metric, aggfunc='sum'
            ).fillna(0)
            x_labels = [str(x) for x in pivot.index.tolist()]
            line_labels = [str(c) for c in pivot.columns.tolist()]
            line_data = [pivot[col].tolist() for col in pivot.columns]
        else:
            # Fallback: GroupBy entity, single series with row index
            grouped = df.groupby(entity_col, as_index=False)[primary_metric].sum()
            x_labels = grouped[entity_col].astype(str).tolist()
            line_labels = [primary_metric]
            line_data = [grouped[primary_metric].tolist()]
        
        n_series = len(line_labels)
        colors = self.DEFAULT_COLORS[:n_series] if n_series <= len(self.DEFAULT_COLORS) else (
            self.DEFAULT_COLORS * ((n_series // len(self.DEFAULT_COLORS)) + 1))[:n_series]
        
        return {
            "line_data": line_data,
            "line_labels": line_labels,
            "line_category": {
                "singular": entity_col,
                "plural": entity_col
            },
            "line_colors": colors,
            "x_labels": x_labels,
            "x_label": temporal_col or entity_col,
            "y_label": primary_metric,
            "img_title": f"{primary_metric} Trend by {entity_col}",
        }
    
    def _adapter_heatmap(self, mt: MasterTable) -> dict:
        """Heatmap: Pivot two categorical dimensions against a metric into a 2-D matrix."""
        df = mt.df
        entity_col, primary_metric, _, _ = self._pick_columns(mt)
        if not entity_col or not primary_metric:
            raise ValueError("Cannot derive heatmap: missing entity or metric column")
        
        # Identify a second categorical dimension (temporal preferred)
        second_dim = None
        for col in df.columns:
            if col == entity_col:
                continue
            if any(kw in col.lower() for kw in ('date', 'time', 'period', 'year', 'month', 'quarter')):
                second_dim = col
                break
        
        if not second_dim:
            # Fallback: use any other categorical column
            cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            others = [c for c in cat_cols if c != entity_col]
            if others:
                second_dim = others[0]
        
        if not second_dim:
            raise ValueError("Cannot derive heatmap: need 2 categorical dimensions")
        
        pivot = df.pivot_table(
            index=second_dim, columns=entity_col,
            values=primary_metric, aggfunc='sum'
        ).fillna(0)
        
        x_labels = [str(c) for c in pivot.columns.tolist()]
        y_labels = [str(r) for r in pivot.index.tolist()]
        heatmap_data = pivot.values.tolist()
        
        return {
            "heatmap_data": heatmap_data,
            "heatmap_category": {
                "singular": primary_metric,
                "plural": primary_metric
            },
            "x_labels": x_labels,
            "y_labels": y_labels,
            "x_label": entity_col,
            "y_label": second_dim,
            "img_title": f"{primary_metric} by {entity_col} and {second_dim}",
        }
    
    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------
    
    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Node C: Generate schemas AND captions.
        
        Mode is determined by ``self.use_relational_adapter``:
        - True  → derive charts from MasterTable using adapter chains (no LLM)
        - False → legacy LLM-based schema mapping
        """
        master_data = state.get("master_data", {})
        
        if self.use_relational_adapter and isinstance(master_data, MasterTable):
            # ===== Relational Adapter mode (DEFAULT) =====
            response = {}
            for chart_type, adapter_fn in [
                ("bar", self._adapter_bar),
                ("scatter", self._adapter_scatter),
                ("pie", self._adapter_pie),
                ("histogram", self._adapter_histogram),
                ("line", self._adapter_line),
                ("heatmap", self._adapter_heatmap),
            ]:
                try:
                    response[chart_type] = adapter_fn(master_data)
                except Exception as e:
                    logger.warning(f"Adapter for {chart_type} failed: {e}. Skipping.")
        else:
            # ===== Legacy mode =====
            # master_data is a dict (old parallel-array format)
            if isinstance(master_data, MasterTable):
                # Convert MasterTable to dict representation for legacy prompt
                master_data_dict = json.loads(master_data.df.to_json(orient='records'))
                data_str = json.dumps(master_data_dict, indent=2)
            elif isinstance(master_data, dict):
                data_str = json.dumps(master_data, indent=2)
            else:
                data_str = str(master_data)
            
            system_prompt = PROMPT_NODE_C_SCHEMA_MAPPER.format(
                master_data_json=data_str
            )
            
            response = self.llm.generate_json(
                system=system_prompt,
                user=f"Transform this Master Data into BAR, SCATTER, PIE, HISTOGRAM, LINE, and HEATMAP chart schemas:\n\n{data_str}",
                temperature=0.9
            )
            
            # Validate each schema (legacy path)
            if isinstance(master_data, dict):
                _legacy_fallbacks = {
                    "bar": (self.validate_bar_schema, self.transform_to_bar),
                    "scatter": (self.validate_scatter_schema, self.transform_to_scatter),
                    "pie": (self.validate_pie_schema, self.transform_to_pie),
                    "histogram": (self.validate_histogram_schema, self.transform_to_histogram),
                    "line": (self.validate_line_schema, self.transform_to_line),
                    "heatmap": (self.validate_heatmap_schema, self.transform_to_heatmap),
                }
                for chart_type, (validator, fallback) in _legacy_fallbacks.items():
                    if chart_type in response:
                        is_valid, errors = validator(response[chart_type])
                        if not is_valid:
                            try:
                                response[chart_type] = fallback(master_data)
                            except Exception as e:
                                logger.warning(f"Legacy fallback for {chart_type} failed: {e}")
        
        state["chart_entries"] = response
        
        # ===== Generate captions for each chart type =====
        captions = {}
        chart_entries = state.get("chart_entries", {})
        
        for chart_type, metadata in chart_entries.items():
            system_prompt = PROMPT_NODE_D_RL_CAPTIONER.format(
                chart_type=chart_type.upper(),
                chart_metadata_json=json.dumps(metadata, indent=2)
            )
            
            caption_response = self.llm.generate_json(
                system=system_prompt,
                user=f"Generate caption for this {chart_type} chart:\n\nMetadata: {json.dumps(metadata, indent=2)}",
                temperature=1.0
            )
            
            cleaned_response = {
                "ground_truth_caption": caption_response.get(
                    "ground_truth_caption", 
                    f"Chart showing {metadata.get('img_title', 'data')}"
                )
            }
            
            is_valid, errors = self.validate_caption_output(cleaned_response)
            if not is_valid:
                print(f"Warning: Caption validation failed for {chart_type}: {errors}")
                cleaned_response["ground_truth_caption"] = f"Chart showing {metadata.get('img_title', 'data')}"
            
            captions[chart_type] = cleaned_response
        
        state["captions"] = captions
        return state

class ChartAgentPipeline:
    """
    Main pipeline orchestrator using LangGraph-style execution.
    
    Complete Workflow:
    Node A: Topic Generation (within user-specified category)
      ↓
    Node B: Data Fabrication (generate CSV → MasterTable)
      ↓
    Node C: Schema Mapping + Caption Generation (adapter chains or legacy LLM)
    
    Config options:
        use_relational_adapter (bool): If True (default), Node C uses relational
            adapter chains. If False, Node C uses legacy LLM-based mapping.
    
    Note: Category must be specified by user (no random selection).
    """
    
    def __init__(self, llm_client, config: Optional[dict] = None):
        self.config = config or {}
        use_adapter = self.config.get("use_relational_adapter", True)
        
        # Initialize nodes
        self.node_a = NodeA_TopicAgent(llm_client)
        self.node_b = NodeB_DataFabricator(llm_client)
        self.node_c = NodeC_SchemaMapper(llm_client, use_relational_adapter=use_adapter)
    
    def create_initial_state(self) -> PipelineState:
        """Create empty initial state"""
        return PipelineState(
            category_id=0,
            category_name="",
            semantic_concept="",
            topic_description="",
            master_data={},
            chart_entries={},
            captions={},
            generation_id=hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat()
        )
    
    def run(self, category_id: int, constraints: Optional[dict] = None) -> PipelineState:
        """
        Execute full pipeline with user-specified category
        
        Args:
            category_id: Category ID (1-30) from META_CATEGORIES
            constraints: Optional constraints for topic generation
                - avoid_concepts: list[str] - Topics to avoid
                - theme_hint: str - Theme suggestion
                - scale_preference: str - "micro" or "macro"
        
        Returns:
            PipelineState with all generated data
        """
        # Validate category_id
        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}\n"
                f"Must be between 1 and 30.\n"
                f"Use get_available_categories() to see all options."
            )
        
        category_name = META_CATEGORIES[category_id - 1]
        
        # Create initial state
        state = self.create_initial_state()
        
        # Node A: Topic Generation (within specified category)
        state = self.node_a(state, category_id, category_name, constraints)
        
        # Node B: Data Fabrication
        state = self.node_b(state)
        
        # Node C: Schema Mapping + Caption Generation (combined)
        state = self.node_c(state)
        
        return state
    
    def run_batch(
        self, 
        category_ids: list[int], 
        constraints_list: Optional[list[dict]] = None
    ) -> list[PipelineState]:
        """
        Run pipeline multiple times for batch generation
        
        Args:
            category_ids: List of category IDs (1-30), one per generation
            constraints_list: Optional list of constraints (one per generation)
        
        Returns:
            List of PipelineState objects
        """
        results = []
        constraints_list = constraints_list or [None] * len(category_ids)
        
        for i, (category_id, constraints) in enumerate(zip(category_ids, constraints_list)):
            try:
                state = self.run(category_id, constraints)
                results.append(state)
            except Exception as e:
                print(f"Generation {i} (category {category_id}) failed: {e}")
                continue
        
        return results


# =============================================================================
# SECTION 6: UNIFIED LLM CLIENT
# =============================================================================

# -----------------------------------------------------------------------------
# Provider Parameter Adapters
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class ProviderCapabilities:
    """Define what parameters each provider supports"""
    supports_temperature: bool = True
    supports_max_tokens: bool = True
    supports_max_completion_tokens: bool = False
    supports_response_format: bool = True
    supports_json_mode: bool = True
    
    # Token parameter name to use
    token_param_name: str = "max_tokens"
    
    # Temperature constraints
    min_temperature: float = 0.0
    max_temperature: float = 2.0
    default_temperature: float = 1.0
    
    # Special handling flags
    requires_json_in_prompt: bool = False
    is_reasoning_model: bool = False


# Provider capability definitions
PROVIDER_CAPABILITIES = {
    "openai": ProviderCapabilities(
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "gemini": ProviderCapabilities(
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,  # Gemini via OpenAI API may not support this
        requires_json_in_prompt=True,
    ),
    "gemini-native": ProviderCapabilities(
        # Gemini native SDK uses different API structure
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
    "azure": ProviderCapabilities(
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "custom": ProviderCapabilities(
        # Conservative defaults for unknown providers
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
}


# Model-specific overrides (for models with special requirements)
MODEL_OVERRIDES = {
    # OpenAI reasoning models have strict parameter limitations
    "o1": ProviderCapabilities(
        supports_temperature=False,  # o1 models don't support temperature
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "o3": ProviderCapabilities(
        supports_temperature=False,
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "gpt-5": ProviderCapabilities(
        supports_temperature=False,  # gpt-5 does not support custom temperature
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
}


def get_provider_capabilities(provider: str, model: str) -> ProviderCapabilities:
    """
    Get capability configuration for a specific provider and model.
    
    Checks model-specific overrides first, then falls back to provider defaults.
    """
    # Check for model-specific overrides
    model_lower = model.lower()
    for model_pattern, capabilities in MODEL_OVERRIDES.items():
        if model_pattern in model_lower:
            return capabilities
    
    # Fall back to provider default
    return PROVIDER_CAPABILITIES.get(provider, PROVIDER_CAPABILITIES["custom"])


class ParameterAdapter:
    """
    Adapts API call parameters to match provider capabilities.
    
    This class ensures that only supported parameters are included in API calls,
    avoiding the need for retry-based error handling.
    """
    
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.capabilities = get_provider_capabilities(provider, model)
    
    def adapt_parameters(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "json"
    ) -> tuple[dict, list[dict]]:
        """
        Adapt parameters to match provider capabilities.
        
        Returns:
            (kwargs, modified_messages): API call kwargs and potentially modified messages
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        
        modified_messages = messages.copy()
        
        # Add temperature if supported
        if self.capabilities.supports_temperature:
            # Clamp temperature to supported range
            clamped_temp = max(
                self.capabilities.min_temperature,
                min(temperature, self.capabilities.max_temperature)
            )
            kwargs["temperature"] = clamped_temp
        
        # Add token limit parameter
        if self.capabilities.supports_max_tokens:
            kwargs[self.capabilities.token_param_name] = max_tokens
        
        # Handle JSON response format
        if response_format == "json":
            if self.capabilities.supports_json_mode and self.capabilities.supports_response_format:
                # Provider supports native JSON mode
                kwargs["response_format"] = {"type": "json_object"}
            elif self.capabilities.requires_json_in_prompt:
                # Add JSON instruction to prompt
                modified_messages = messages.copy()
                modified_messages[-1] = modified_messages[-1].copy()
                modified_messages[-1]["content"] += (
                    "\n\nRespond with valid JSON only, no markdown formatting."
                )
        
        return kwargs, modified_messages


# -----------------------------------------------------------------------------
# Unified LLM Client
# -----------------------------------------------------------------------------

class LLMClient:
    """
    Unified LLM client supporting multiple providers with proper parameter adaptation.
    
    Supported providers:
    - OpenAI: GPT-4, GPT-3.5-turbo, o1, etc.
    - Gemini: gemini-1.5-pro, gemini-2.0-flash, etc. (via OpenAI SDK)
    - Gemini Native: Using google-genai SDK
    - Azure OpenAI: Azure-hosted OpenAI models
    - Custom: Any OpenAI API-compatible service
    
    Usage:
        # OpenAI
        client = LLMClient(api_key="sk-...", model="gpt-4", provider="openai")
        
        # Gemini (via OpenAI API)
        client = LLMClient(
            api_key="your-gemini-key", 
            model="gemini-2.0-flash-lite",
            provider="gemini"
        )
        
        # Gemini (native SDK)
        client = LLMClient(
            api_key="your-gemini-key",
            model="gemini-2.0-flash-lite", 
            provider="gemini-native"
        )
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gemini-2.0-flash-lite",
        base_url: Optional[str] = None,
        provider: str = "auto"
    ):
        """
        Initialize LLM client with automatic parameter adaptation.
        
        Args:
            api_key: API key for the provider
            model: Model name
            base_url: Custom API endpoint URL (optional)
            provider: Provider type ("auto", "openai", "gemini", "gemini-native", "azure", "custom")
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None
        self._native_client = None
        
        # Auto-detect provider from model name if needed
        if provider == "auto":
            # FIXME：If model name contains "gemini", now will go to gemini-native, might use Gemini via OpenAI API in the future
            if "gemini" in model.lower():
                self.provider = "gemini-native"  # Default to native SDK
            elif "gpt" in model.lower() or "o1" in model.lower() or "o3" in model.lower():
                self.provider = "openai"
            elif "claude" in model.lower():
                self.provider = "openai"  # Claude via compatibility layer
            else:
                self.provider = "custom"
        else:
            self.provider = provider
        
        # Initialize parameter adapter
        self.adapter = ParameterAdapter(self.provider, self.model)
        
        # Set base URL based on provider
        if self.provider == "gemini":
            # Gemini via OpenAI SDK
            if not self.base_url:
                self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif self.provider == "gemini-native":
            # Native Gemini SDK doesn't use base_url
            self.base_url = None
        elif self.provider == "openai" and not self.base_url:
            self.base_url = "https://api.openai.com/v1"
    
    def _ensure_client(self):
        """Lazy initialization of API client"""
        if self.provider == "gemini-native":
            # Use native Gemini SDK
            if self._native_client is None:
                try:
                    from google import genai
                    self._native_client = genai.Client(api_key=self.api_key)
                except ImportError:
                    raise ImportError(
                        "Please install google-genai for native Gemini support: "
                        "pip install google-genai"
                    )
        else:
            # Use OpenAI SDK for all other providers
            if self._client is None:
                try:
                    from openai import OpenAI
                    self._client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                except ImportError:
                    raise ImportError(
                        "Please install openai SDK: pip install openai>=1.0.0"
                    )
    
    def generate(
        self, 
        system: str, 
        user: str, 
        temperature: float = 0.7,
        max_tokens: int = 4096, 
        response_format: str = "json"
    ) -> str:
        """
        Generate text response using the configured LLM.
        
        Parameters are automatically adapted to match provider capabilities.
        
        Args:
            system: System prompt
            user: User prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum response length
            response_format: "json" or "text"
        
        Returns:
            Generated text response
        """
        self._ensure_client()
        
        if self.provider == "gemini-native":
            # Use Gemini native SDK
            full_prompt = f"{system}\n\n---\n\n{user}"
            
            # Prepare generation config
            generation_config = {}
            if self.adapter.capabilities.supports_temperature:
                generation_config["temperature"] = temperature
            if self.adapter.capabilities.supports_max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Add JSON instruction if needed
            if response_format == "json" and self.adapter.capabilities.requires_json_in_prompt:
                full_prompt += "\n\nRespond with valid JSON only, no markdown formatting."
            
            response = self._native_client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=generation_config
            )
            
            return response.text
        else:
            # Use OpenAI SDK (for OpenAI, Gemini via OpenAI API, Azure, etc.)
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
            
            # Use parameter adapter to get correct kwargs
            kwargs, modified_messages = self.adapter.adapt_parameters(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            # Update kwargs with modified messages
            kwargs["messages"] = modified_messages
            
            # Single API call with properly adapted parameters (no retry needed)
            response = self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
    
    def generate_json(self, system: str, user: str, **kwargs) -> dict:
        """Generate and parse JSON response"""
        response = self.generate(system, user, response_format="json", **kwargs)
        
        # Clean response (remove potential markdown code blocks)
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            # Provide detailed error information
            raise ValueError(
                f"Failed to parse JSON response from {self.provider} "
                f"(model: {self.model}). Error: {e}\n"
                f"Response preview: {cleaned[:500]}"
            )


# 为了向后兼容，保留 GeminiClient 作为别名
class GeminiClient(LLMClient):
    """
    向后兼容的 Gemini 客户端
    
    使用 Gemini 原生 SDK（google-genai）
    """
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__(
            api_key=api_key,
            model=model,
            provider="gemini-native"
        )


# =============================================================================
# SECTION 7: UTILITY FUNCTIONS
# =============================================================================

def generate_unique_id(prefix: str = "gen") -> str:
    """Generate unique ID for tracking generations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(random.random()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}"


def validate_category(category: str) -> bool:
    """Check if category is in valid taxonomy"""
    return category in META_CATEGORIES


def get_category_by_id(category_id: int) -> Optional[str]:
    """Get category name by ID (1-30)"""
    if 1 <= category_id <= 30:
        return META_CATEGORIES[category_id - 1]
    return None


def get_available_categories() -> list[str]:
    """
    Get list of all available categories for manual topic selection.
    
    Returns:
        List of 30 predefined category strings
    
    Example:
        >>> categories = get_available_categories()
        >>> print(categories[0])
        "1 - Media & Entertainment"
        >>> 
        >>> # Use with pipeline
        >>> pipeline.run(category=categories[0])
    """
    return META_CATEGORIES.copy()


def print_available_categories():
    """
    Print all available categories in a formatted list.
    
    Useful for interactive category selection.
    """
    print("可用的 30 个主题类别:")
    print("=" * 60)
    for i, category in enumerate(META_CATEGORIES, 1):
        print(f"{i:2d}. {category}")
    print("=" * 60)
    print("\n使用方法:")
    print("  # 使用类别编号 (1-30)")
    print("  pipeline.run(category_id=1)  # Media & Entertainment")
    print("  ")
    print("  # 批量生成，指定多个类别")
    print("  pipeline.run_batch(category_ids=[1, 4, 10, 15])")
    print("  ")
    print("  # 在 example_runner.py 中使用")
    print("  python example_runner.py --category 1 --count 5")


def format_for_metadata_file(chart_type: str, func_id: str, category: str, entry: dict) -> str:
    """Format a single entry for insertion into metadata.py"""
    entry_str = json.dumps(entry, indent=12)
    # Adjust indentation for nested structure
    lines = entry_str.split('\n')
    formatted_lines = [lines[0]] + ['        ' + line for line in lines[1:]]
    return '\n'.join(formatted_lines)


if __name__ == "__main__":
    # Example usage demonstration
    print("ChartAgentVAGEN Pipeline Architecture")
    print("=" * 50)
    print(f"Categories: {len(META_CATEGORIES)}")
    print(f"Chart Types: {[ct.value for ct in ChartType]}")
    print("\nTo use this pipeline:")
    print("1. Initialize LLMClient or GeminiClient with your API key")
    print("2. Create ChartAgentPipeline instance")
    print("3. Call pipeline.run() or pipeline.run_batch()")
    print("\nSupported LLM providers:")
    print("- OpenAI (GPT-4, GPT-3.5)")
    print("- Google Gemini (via native SDK or OpenAI-compatible API)")
    print("- Azure OpenAI")
    print("- Custom endpoints (any OpenAI-compatible service)")
